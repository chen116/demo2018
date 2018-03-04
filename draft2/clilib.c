#include <stdio.h>
#include <heartbeats/heartbeat.h>
#include <sys/ipc.h>

#define SHMSZ     27

void write_vlog(_heartbeat_record_t*,_HB_global_state_t*, int);

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
   for(int i = 0; i < 261;i++){
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