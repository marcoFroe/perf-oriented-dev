#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned long dn;

dn delannoy(dn x, dn y) {
	if(x == 0 || y == 0) return 1;

	dn* dp = malloc((x + 1) * sizeof(*dp));
	if(dp == NULL) {
		fprintf(stderr, "Memory allocation failed\n");
		exit(EXIT_FAILURE);
	}

	for(dn i = 0; i <= x; ++i)
		dp[i] = 1;

	for(dn j = 1; j <= y; ++j) {
		dn prev_diag = 1;

		for(dn i = 1; i <= x; ++i) {
			dn temp = dp[i];

			dp[i] = dp[i] + dp[i - 1] + prev_diag;

			prev_diag = temp;
		}
	}

	dn result = dp[x];
	free(dp);
	return result;
}

dn DELANNOY_RESULTS[] = { 1,
	                      3,
	                      13,
	                      63,
	                      321,
	                      1683,
	                      8989,
	                      48639,
	                      265729,
	                      1462563,
	                      8097453,
	                      45046719,
	                      251595969,
	                      1409933619,
	                      7923848253,
	                      44642381823,
	                      252055236609,
	                      1425834724419,
	                      8079317057869,
	                      45849429914943,
	                      260543813797441,
	                      1482376214227923,
	                      8443414161166173 };

int NUM_RESULTS = sizeof(DELANNOY_RESULTS) / sizeof(dn);

int main(int argc, char** argv) {
	if(argc < 2) {
		printf("Usage: delannoy N [+t]\n");
		exit(-1);
	}

	int n = atoi(argv[1]);
	if(n >= NUM_RESULTS) {
		printf("N too large (can only check up to %d)\n", NUM_RESULTS);
		exit(-1);
	}

	dn result = 0;
	result = delannoy(n, n);

	if(result == DELANNOY_RESULTS[n]) {
		printf("Verification: OK\n");
		return EXIT_SUCCESS;
	}
	printf("Verification: ERR\n");
	return EXIT_FAILURE;
}
