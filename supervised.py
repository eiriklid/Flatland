correct_choice = [1 if teacher_tile == neighbours[i] else 0 for i in range(3)]
exp_output = [math.exp(y_i) for y_i in output]
exp_output_sum = sum(exp_output)
delta = [correct_choice[i]-(exp_output[i]/exp_output_sum) for i in range(len(output))]
