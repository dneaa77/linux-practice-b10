#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>
#include <sys/mman.h>
#include <string.h>

static double elapsed(struct timespec a,struct timespec b){return (b.tv_sec-a.tv_sec)*1000.0+(b.tv_nsec-a.tv_nsec)/1e6;}
int main(int argc,char **argv){
    size_t bytes=128ULL*1024*1024;
    long page=sysconf(_SC_PAGESIZE);
    if(page<=0){perror("sysconf");return 1;}
    int huge=argc>1 && strcmp(argv[1],"--huge")==0;
    unsigned char *p=mmap(NULL,bytes,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if(p==MAP_FAILED){perror("mmap");return 1;}
    if(huge){if(madvise(p,bytes,MADV_HUGEPAGE)!=0)perror("madvise");}
    else {if(madvise(p,bytes,MADV_NOHUGEPAGE)!=0)perror("madvise");}
    for(size_t i=0;i<bytes;i+=(size_t)page)p[i]=1;
    const size_t strides[]={64,(size_t)page};
    volatile uint64_t sink=0;
    for(int s=0;s<2;s++){
        size_t stride=strides[s];
        struct timespec start,end;
        clock_gettime(CLOCK_MONOTONIC,&start);
        for(int round=0;round<8;round++)for(size_t i=0;i<bytes;i+=stride)sink+=p[i];
        clock_gettime(CLOCK_MONOTONIC,&end);
        printf("huge_requested=%d stride=%zu bytes=%zu accesses=%zu time_ms=%.3f sink=%llu\n",huge,stride,bytes,8*(bytes/stride),elapsed(start,end),(unsigned long long)sink);
    }
    puts("Note: MADV_HUGEPAGE is a hint, not proof that huge pages were allocated.");
    munmap(p,bytes);return 0;
}
