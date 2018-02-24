/*
 * shm-client - client program to demonstrate shared memory.
 */
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdio.h>
#include <heartbeats/heartbeat.h>



#define SHMSZ     27

int main(int argc, char **argv)

{
    _heartbeat_record_t* p = NULL;
    _HB_global_state_t* g = NULL;

    int shmid,shmidg;
    key_t key;


    /*
     * We need to get the segment named
     * "5678", created by the server.
     */
    key = 1234<<1;

    /*
     * Locate the segment.
     */
    if ((shmid = shmget(key, SHMSZ, 0666)) < 0) {
        perror("shmget");
        exit(1);
    }
    if ((shmidg = shmget(key|1, SHMSZ, 0666)) < 0) {
        perror("shmget");
        exit(1);
    }
    /*
     * Now we attach the segment to our data space.
     */
    p = (_heartbeat_record_t*) shmat(shmid, NULL, 0); // p = hb->log
    g = (_heartbeat_record_t*) shmat(shmidg, NULL, 0); // g = hb->state
    // if ((shm = shmat(shmid, NULL, 0)) == (char *) -1) {
    //     perror("shmat");
    //     exit(1);
    // }

    for (int i = 0; i < 261; ++i)
    {
        /* code */
    
    printf("%lld    %d    %lld    %f    %f    %f\n",
          (long long int) p[i].beat,
          p[i].tag,
          (long long int) p[i].timestamp,
          p[i].global_rate,
          p[i].window_rate,
          p[i].instant_rate);
}
printf("%d    %d    %d   %f   %f\n",
      g->buffer_index,
      g->counter,
      g->read_index,
        g->min_heartrate,
      g->max_heartrate);
    // /*
    //  * Now read what the server put in the memory.
    //  */
    // for (s = shm; *s != NULL; s++)
    //     putchar(*s);
    // putchar('\n');

    /*
     * Finally, change the first character of the 
     * segment to '*', indicating we have read 
     * the segment.
     */
    //*shm = '*';

    exit(0);
}
