#include <stdio.h>
#include <heartbeats/heartbeat.h>
#include <sys/ipc.h>
#include <sys/types.h>
#include <sys/shm.h>



// #include <heartbeat-util-shared.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

void setshm_glo(key_t);
void setshm_log(key_t,int64_t);
void write_vlog(_heartbeat_record_t*,_HB_global_state_t*, int);
int get_hr(_heartbeat_record_t*, int);
static void hb_flush_buffer(heartbeat_t volatile * );
static float hb_window_average(heartbeat_t volatile * ,int64_t );
int64_t get_ts(_heartbeat_record_t*, int);
_heartbeat_record_t* HB_alloc_log(int , int64_t );
_HB_global_state_t* HB_alloc_state(int );

int anchors_heartbeat_finish(int) ;
int64_t anchors_heartbeat( int, int );
int get_index(_HB_global_state_t*);
int get_hr_from_hb(int , int);

int anchors_heartbeat_init(int,int64_t,int64_t ,const char* , double ,double );
int get_index(_HB_global_state_t* g)
{
	return g->read_index;
}
int get_hr(_heartbeat_record_t* p,int index)
{
	return p[index].instant_rate*1000000;
}
int get_hr_from_hb(int hb_shm_id, int index)
{
int shmid;
  if ((shmid = shmget(hb_shm_id, 1*sizeof(heartbeat_t), 0666)) < 0) {
        perror("shmget");
        return 0;
    }
  heartbeat_t* hb = (heartbeat_t*) shmat(shmid, NULL, 0);
  return hb->log[index].instant_rate*1000000;


}

int64_t get_ts(_heartbeat_record_t* p,int index)
{                                          

 // return p[index].timestamp%10000;
  return p[index].timestamp;
  //return p[index].timestamp;
}
void write_vlog(_heartbeat_record_t* p,_HB_global_state_t* g, int fname_index)
{ 
    FILE * fp;
    char * str1 = "vlog";
    char str2[10];
    sprintf(str2, "%d", fname_index);   
    char * str3 = (char *) malloc(1 + strlen(str1)+ strlen(str2) );
    strcpy(str3, str1);
    strcat(str3, str2);
    /* open the file for writing*/
    fp = fopen (str3,"w");

 
   /* write 10 lines of text into the file stream*/
   //for(int i = 0; i < g->buffer_index;i++){
   for(int i = 0; i < 51;i++){
    fprintf(fp,"%lld    %d    %lld    %f    %f    %f\n",
          (long long int) p[i].beat,
          p[i].tag,
          (long long int) p[i].timestamp,
          p[i].global_rate,
          p[i].window_rate,
          p[i].instant_rate);
   }
 
   /* close the file*/  
   fclose (fp);
   return;

// printf("%d    %d    %d   %f   %f\n",
//       g->buffer_index,
//       g->counter,
//       g->read_index,
//         g->min_heartrate,
//       g->max_heartrate);

//    return g->counter;
}

void setshm_glo(key_t key)
{

    // key_t key;
    int shmid;

    if ((shmid = shmget(key, 1*sizeof(_HB_global_state_t), IPC_CREAT | 0666)) < 0) {
         perror("shmget");
        // printf("%s",strerror(errno));
        perror("Error in Shared Memory get statement");
        //shmid = shmget(key, SHMSIZE, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH | IPC_CREAT);
        if (shmid == -1)  {
                // printf("%s",strerror(errno));
                perror("Error in Shared Memory get statement");
                exit(1);
        }
 
    }
    return;

}
void setshm_log(key_t key, int64_t buffer_size )
{

    // key_t key;
    int shmid;

    if ((shmid = shmget(key, buffer_size*sizeof(_heartbeat_record_t), IPC_CREAT | 0666)) < 0) {
         perror("shmget");
        // printf("%s",strerror(errno));
        perror("Error in Shared Memory get statement");
        //shmid = shmget(key, SHMSIZE, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH | IPC_CREAT);
        if (shmid == -1)  {
                // printf("%s",strerror(errno));
                perror("Error in Shared Memory get statement");
                exit(1);
        }
 
    }
    return;

}


int anchors_heartbeat_init(int hb_shm_id,int64_t window_size,
                            int64_t buffer_depth,
                            const char* log_name,
                            double min_target,
                            double max_target) {
  int pid = getpid();

  char* enabled_dir;
    int shmid;

if ((shmid = shmget(hb_shm_id, 1*sizeof(heartbeat_t), IPC_CREAT | 0666)) < 0) {
  return 0; 
    }

heartbeat_t* hb = NULL;
hb = (heartbeat_t*) shmat(shmid, NULL, 0); 

  if (hb == NULL) {
    perror("Failed to malloc heartbeat");
    return 0;
  }
  // set to NULL so free doesn't fail in finish function if we have to abort
  hb->window = NULL;
  hb->text_file = NULL;

  
  hb->state = HB_alloc_state(hb_shm_id);

  if (hb->state == NULL) {
    printf("meow\n");
    anchors_heartbeat_finish(hb_shm_id);
    return 0;
  }
  hb->state->pid = pid;

  if(log_name != NULL) {
    hb->text_file = fopen(log_name, "w");
    if (hb->text_file == NULL) {
      perror("Failed to open heartbeat log file");
      anchors_heartbeat_finish(hb_shm_id);
      return 0;
    } else {
      fprintf(hb->text_file, "Beat    Tag    Timestamp    Global Rate    Window Rate    Instant Rate\n" );
    }
  } else {
    hb->text_file = NULL;
  }

  enabled_dir = getenv("HEARTBEAT_ENABLED_DIR");
  if(!enabled_dir) {
    anchors_heartbeat_finish(hb_shm_id);
    return 0;
  }
  snprintf(hb->filename, sizeof(hb->filename), "%s/%d", enabled_dir, hb->state->pid);
  printf("%s\n", hb->filename);

  // hb->log = HB_alloc_log(hb->state->pid, buffer_depth);
  

  hb->log = HB_alloc_log(hb_shm_id, buffer_depth);



  if(hb->log == NULL) {
    anchors_heartbeat_finish(hb_shm_id);
    return 0;
  }

  hb->first_timestamp = hb->last_timestamp = -1;
  hb->state->window_size = window_size;
  hb->window = (int64_t*) malloc((size_t)window_size * sizeof(int64_t));
  if (hb->window == NULL) {
    perror("Failed to malloc window size");
    anchors_heartbeat_finish(hb_shm_id);
    return 0;
  }
  hb->current_index = 0;
  hb->state->min_heartrate = min_target;
  hb->state->max_heartrate = max_target;
  hb->state->counter = 0;
  hb->state->buffer_index = 0;
  hb->state->read_index = 0;
  hb->state->buffer_depth = buffer_depth;
  pthread_mutex_init(&hb->mutex, NULL);
  hb->steady_state = 0;
  hb->state->valid = 0;

  hb->binary_file = fopen(hb->filename, "w");
  if ( hb->binary_file == NULL ) {
    perror("Failed to open heartbeat log");
    anchors_heartbeat_finish(hb_shm_id);
    return 0;
  }
  fclose(hb->binary_file);

  return 1;
}
int anchors_heartbeat_finish(int hb_shm_id) {
    int shmid;

    if ((shmid = shmget(hb_shm_id, 1*sizeof(heartbeat_t), 0666)) < 0) {
        perror("shmget");
        printf("meow\n");
        return 0;
    }
  heartbeat_t* hb = (heartbeat_t*) shmat(shmid, NULL, 0);
  if (hb != NULL) {
    pthread_mutex_destroy(&hb->mutex);
    free(hb->window);
    if(hb->text_file != NULL) {
      hb_flush_buffer(hb);
      fclose(hb->text_file);
    }
    remove(hb->filename);
    /*TODO : need to deallocate log */
    free(hb);
  }
  return 1;
}

int64_t anchors_heartbeat( int hb_shm_id, int tag )
{
    int shmid;

  if ((shmid = shmget(hb_shm_id, 1*sizeof(heartbeat_t), 0666)) < 0) {
        perror("shmget");
        return 0;
    }
  heartbeat_t* hb = (heartbeat_t*) shmat(shmid, NULL, 0);

    struct timespec time_info;
    int64_t time;
    int64_t old_last_time;

    pthread_mutex_lock(&hb->mutex);
    //printf("Registering Heartbeat\n");
    old_last_time = hb->last_timestamp;
    clock_gettime( CLOCK_REALTIME, &time_info );
    time = ( (int64_t) time_info.tv_sec * 1000000000 + (int64_t) time_info.tv_nsec );
    hb->last_timestamp = time;

    if(hb->first_timestamp == -1) {
      //printf("In heartbeat - first time stamp\n");
      hb->first_timestamp = time;
      hb->last_timestamp  = time;
      hb->window[0] = 0;

      //printf("             - accessing state and log\n");
      hb->log[0].beat = hb->state->counter;
      hb->log[0].tag = tag;
      hb->log[0].timestamp = time;
      hb->log[0].window_rate = 0;
      hb->log[0].instant_rate = 0;
      printf("meow meow\n");
      hb->log[0].global_rate = 0;
      hb->state->counter++;
      hb->state->buffer_index++;
      hb->state->valid = 1;
    }
    else {
      //printf("In heartbeat - NOT first time stamp - read index = %d\n",hb->state->read_index );
      int64_t index =  hb->state->buffer_index;
      hb->last_timestamp = time;
      double window_heartrate = hb_window_average(hb, time-old_last_time);
      double global_heartrate =
  (((double) hb->state->counter+1) /
   ((double) (time - hb->first_timestamp)))*1000000000.0;
      double instant_heartrate = 1.0 /(((double) (time - old_last_time))) *
  1000000000.0;

      hb->log[index].beat = hb->state->counter;
      hb->log[index].tag = tag;
      hb->log[index].timestamp = time;
      hb->log[index].window_rate = window_heartrate;
      hb->log[index].instant_rate = instant_heartrate;


      hb->log[index].global_rate = global_heartrate;
      hb->state->buffer_index++;
      hb->state->counter++;
      hb->state->read_index++;

      if(hb->state->buffer_index%hb->state->buffer_depth == 0) {
  if(hb->text_file != NULL)
    hb_flush_buffer(hb);
  hb->state->buffer_index = 0;
      }
      if(hb->state->read_index%hb->state->buffer_depth == 0) {
  hb->state->read_index = 0;
      }
    }
    pthread_mutex_unlock(&hb->mutex);
    return time;

}
static float hb_window_average(heartbeat_t volatile * hb,
              int64_t time) {
  int i;
  double average_time = 0;
  double fps;


  if(!hb->steady_state) {
    hb->window[hb->current_index] = time;

    for(i = 0; i < hb->current_index+1; i++) {
      average_time += (double) hb->window[i];
    }
    average_time = average_time / ((double) hb->current_index+1);
    hb->last_average_time = average_time;
    hb->current_index++;
    if( hb->current_index == hb->state->window_size) {
      hb->current_index = 0;
      hb->steady_state = 1;
    }
  }
  else {
    average_time =
      hb->last_average_time -
      ((double) hb->window[hb->current_index]/ (double) hb->state->window_size);
    average_time += (double) time /  (double) hb->state->window_size;

    hb->last_average_time = average_time;

    hb->window[hb->current_index] = time;
    hb->current_index++;

    if( hb->current_index == hb->state->window_size)
      hb->current_index = 0;
  }
  fps = (1.0 / (float) average_time)*1000000000;

  return (float)fps;
}
static void hb_flush_buffer(heartbeat_t volatile * hb) {
  int64_t i;
  int64_t nrecords = hb->state->buffer_index; // buffer_depth

  //printf("Flushing buffer - %lld records\n",
  //   (long long int) nrecords);

  if(hb->text_file != NULL) {
    for(i = 0; i < nrecords; i++) {
      fprintf(hb->text_file,
        "%lld    %d    %lld    %f    %f    %f\n",
        (long long int) hb->log[i].beat,
        hb->log[i].tag,
        (long long int) hb->log[i].timestamp,
        hb->log[i].global_rate,
        hb->log[i].window_rate,
        hb->log[i].instant_rate);
    }

    fflush(hb->text_file);
  }
}


_heartbeat_record_t* HB_alloc_log(int pid, int64_t buffer_size) {
  _heartbeat_record_t* p = NULL;
  int shmid;

  printf("Allocating log for %d, %d\n", pid, pid << 1);

  shmid = shmget(pid << 1, buffer_size*sizeof(_heartbeat_record_t), IPC_CREAT | 0666);
  if (shmid < 0) {
    perror("cannot allocate shared memory for heartbeat records");
    return NULL;
  }

  /*
   * Now we attach the segment to our data space.
   */
  p = (_heartbeat_record_t*) shmat(shmid, NULL, 0);
  if (p == (_heartbeat_record_t*) -1) {
    perror("cannot attach shared memory to heartbeat enabled process");
    return NULL;
  }

  return p;
}

_HB_global_state_t* HB_alloc_state(int pid) {
  _HB_global_state_t* p = NULL;
  int shmid;

  shmid = shmget((pid << 1) | 1, 1*sizeof(_HB_global_state_t), IPC_CREAT | 0666);
  if (shmid < 0) {
    perror("cannot allocate shared memory for heartbeat global state");
    return NULL;
  }

  /*
   * Now we attach the segment to our data space.
   */
  p = (_HB_global_state_t*) shmat(shmid, NULL, 0);
  if (p == (_HB_global_state_t*) -1) {
    perror("cannot attach shared memory to heartbeat global state");
    return NULL;
  }

  return p;
}