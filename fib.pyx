def is_repfibdigit(number_to_test):
	answer = False
	n = map(int,str(number_to_test))
	while number_to_test > n[0]:
		n=n[1:]+[sum(n)]
	if (number_to_test == n[0]) & (number_to_test>9): answer = True
	return answer
