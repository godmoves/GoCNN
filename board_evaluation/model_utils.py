#!/usr/bin/env python2


def print_info(feature_cube=None, y_pred=None, y_val=None, y_true=None, board_size=19):
    '''
        Visual the outputs of the model.
        Feature_cube: the x input of model, currently assumes first 6 planes are board position features
        y_pred:       board_size x board_size matrix of thresholded prediction of final board ownership
        y_val:        board_size x board_size matrix of probabilities output by model
        y_true:       board_size x board_size matrix of true board ownership
        board_size:   board size
    '''
    error_count = 0
    for i in reversed(range(board_size)):
        current_row = ""
        if feature_cube is not None:
            for j in range(board_size):
                b_sum = feature_cube[i][j][0] + feature_cube[i][j][1] + feature_cube[i][j][2]
                w_sum = feature_cube[i][j][3] + feature_cube[i][j][4] + feature_cube[i][j][5]
                if b_sum > 0:
                    current_row += '1'
                elif w_sum > 0:
                    current_row += '0'
                else:
                    current_row += '*'
            current_row += "   "
        if y_pred is not None:
            for j in range(board_size):
                if y_pred[i][j] == 1:
                    current_row += '1'
                elif y_pred[i][j] == 0:
                    current_row += '0'
                else:
                    current_row += '*'
            current_row += "   "
        if y_val is not None:
            for j in range(board_size):
                val = round(10 * y_val[i][j])
                if val >= 10:
                    val = 9
                current_row += "%d" % val
            current_row += "   "
        if y_true is not None:
            for j in range(board_size):
                if y_true[i][j] == 1:
                    current_row += '1'
                elif y_true[i][j] == 0:
                    current_row += '0'
                else:
                    current_row += '*'
            current_row += "   "
        if y_pred is not None and y_true is not None:
            for j in range(board_size):
                if y_pred[i][j] == y_true[i][j]:
                    current_row += '.'
                else:
                    current_row += 'X'
                    error_count += 1
        print(current_row)
    return error_count


def test_accuracy(features, targets, model):
    # I get a memory error when tf tries to feed the whole test set into my GPU, so we will do it in batches
    BATCH_SIZE = 128
    NUM_SAMPLES = len(features)
    batch_idx = 0

    x = model.x
    y_real = model.y_real
    correct_count_op = model.correct_count
    board_size = model.board_size

    num_correct = 0
    while batch_idx < NUM_SAMPLES:
        x_ = features[batch_idx:batch_idx + BATCH_SIZE]
        y_ = targets[batch_idx:batch_idx + BATCH_SIZE]
        num_correct += correct_count_op.eval(feed_dict={x: x_, y_real: y_})
        batch_idx += BATCH_SIZE
    return float(num_correct) / float(NUM_SAMPLES * board_size * board_size)
