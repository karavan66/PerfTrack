#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <omp.h>

void main(int argc, char * argv[])
{
	float **array1, **array2,**array3,cnt=1;
	int nrows, ncolumns,i,j,k;
	
	
	if(argc<2)
{
	printf("\nPlease enter carrect argumets <dimensions>");
	exit(0);
}

	nrows=atoi(argv[1]);
	ncolumns=atoi(argv[1]);
	
	array1 = malloc(nrows * sizeof(float *));
	if(array1 == NULL)
		{
		printf("out of memory\n");
		exit(0);
		}
	for(i = 0; i < nrows; i++)
		{
		array1[i] = malloc(ncolumns * sizeof(float));
		if(array1[i] == NULL)
			{
			printf("out of memory\n");
			exit(0);
			}
		}
	
	for(i=0;i<nrows;i++)
	{
		for(j=0;j<ncolumns;j++)
		{
			array1[i][j]=cnt;
			//printf("%u ",array1[i][j]);
			cnt++;
		}
		//printf("\n");
	}

	cnt=1;
	
	array2 = malloc(nrows * sizeof(float *));
	if(array2 == NULL)
		{
		printf("out of memory\n");
		exit(0);
		}
	for(i = 0; i < nrows; i++)
		{
		array2[i] = malloc(ncolumns * sizeof(float));
		if(array2[i] == NULL)
			{
			printf("out of memory\n");
			exit(0);
			}
		}
	
	for(i=0;i<nrows;i++)
	{
		for(j=0;j<ncolumns;j++)
		{
			array2[i][j]=cnt;
			//printf("%u ",array2[i][j]);
			cnt++;
		}
		//printf("\n");
	}	
		
		
	array3 = malloc(nrows * sizeof(float *));
	if(array3 == NULL)
		{
		printf("out of memory\n");
		exit(0);
		}
	for(i = 0; i < nrows; i++)
		{
		array3[i] = malloc(ncolumns * sizeof(float));
		if(array3[i] == NULL)
			{
			printf("out of memory\n");
			exit(0);
			}
		}	
		
	for(i=0;i<nrows;i++)
	{
		for(j=0;j<ncolumns;j++)
		{
			array3[i][j]=0;
			//printf("%u ",array2[i][j]);
		}
	}


		
	#pragma omp parallel for num_threads(8) private(i,j,k)
	for(i=0;i<nrows;i++)
	//#pragma omp parallel for num_threads(10) private(j,k)
	for(j=0;j<ncolumns;j++)
		for(k=0;k<nrows;k++)
		{
				
		    int ii = rand() % nrows;
                    int jj = rand() % ncolumns;
                    int kk = rand() % nrows;
				
			//row major order multiplication
			//array3[i][j]=array3[i][j]+ (array1[i][k]*array2[k][j]);
			//column major order multiplication
			//array3[j][i]=array3[j][i]+ (array1[j][k]*array2[k][i]);
			array3[jj][ii]=array3[jj][ii]+ (array1[jj][kk]*array2[kk][ii]);

		}	

	for(i=0;i<nrows;i++)
	{
		for(j=0;j<ncolumns;j++)
		{
			printf("%f ",array3[i][j]);
		}
		printf("\n");
	}	
			
}
