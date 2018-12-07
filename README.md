# Using CNN for Go board evaluation with tensorflow

![travisci](https://travis-ci.com/godmoves/GoCNN.svg?branch=master)

This is code for training and evaluating a Convolutional Neural Network for
board evaluation in Go. This is an ongoing project and I will be adding to it
in the coming weeks. In this project we use CNN to predict the final state of the board. This is possible due to the nature of the game Go, because pieces do not move during the game, early and midgame board positions are highly predictive of the final ownership. The model exhibited here would likely perform poorly, but it is still interesting to see what it learned and I hope this work will inspire future projects.

## Current Model

### Feature Planes

The inputs to the model are 8 feature planes containing information about the
current state of the board. 
```
0: our stones with 1 liberty
1: our stones with 2 liberty
2: our stones with 3 or more liberties
3: their stones with 1 liberty
4: their stones with 2 liberty
5: their stones with 3 or more liberty
6: simple ko
7: color to move, 1 for black and 0 for white
```
The target is a 19x19 binary matrix, where 1 indicates the player to move owns the location as either territory or has a stone on the location at the end of the game, 0 indicates the other player. In seki situations we consider both groups alive, and randomly assign spaces in between stones. We use GNU-Go to remove dead stones from the board and determine final ownership. Training only on games not ending in resignation are likely to **introduce unwanted biases** to the model (e.g. large groups are more likely to live and all games are close), future work should address this issue.

### NN Architecture

So far I have only tried a single architecture; namely a 5-layer 64-filter CNN. It achieves 90% accuracy on a test set (the training set contains 350k games from CGOS and test set consists of 3500 games not used in training). The convolution sizes are all 5x5 and the number of filters in each layer are 64. The final output layer is a single 5x5 convolution. I use rectified linear units for activations in between each layer.

### Output

The output of the model is a vector of 361 probabilities, one for each space in
the board, and is the probability that the player to move will occupy that space at the end of the game. We use a sigmoid activation for the output layer and minimize the sum of squares loss between the predicted probabilities and the actual binary target. 

### Optimizer

We use an ADAM optimizer with learning rate 10e-4.

## Training Pipeline

1. Create a separate environment for GoCNN (optional)
```
conda create -n gocnn python=2.7
source activate gocnn
```

2. Install what is needed:  
The following packages are required by the training code:

- gomill
- matplotlib
- pandas
- numpy
- tqdm
- TensorFlow

Just install install them by: 
```
pip install -r requirements.txt
```
You can install a GPU version of TensorFlow if you have a decent GPU, or just install the CPU version.
```
# For CPU version
pip install tensorflow

# For GPU version
pip install tensorflow_gpu
```

3. Build GnuGo. GnuGo is used to remove the dead stones from the board, you can build is by using this command;
    ```
    bash ./thirdparty/build_gnugo.sh
    ```

4. Get training data. You can use your own collected sgf files and put them all into `./data/raw`, or just download [CGOS 9x9 Go data](http://www.yss-aya.com/cgos/9x9/archive.html) using:
```
python main.py download
```

5. Preprocess data. This will pick out the sgfs that can be used in our NN training, and convert them into the target format we mentioned in feature part.
```
python main.py preprocess
```

6. Split data into training and test set. By default, 1% games are split into test set and not used to train the network.
```
bash ./data/input/move_to_test.sh
```

7. Start the training.
```
python main.py train
```

8. After the training finished, you can check out your training result by running the program in GTP mode and play with it interactively through [GoGui](https://sourceforge.net/projects/gogui/):
```
python main.py gtp
```

### Some Tips

For more information about the training settings, you can check it by `python main.py -h`.

## Third party libraries/software used
* Modified some code from
[kgsgo-dataset-preprocessor](https://github.com/hughperkins/kgsgo-dataset-preprocessor)
to do data munging.
* [Gomill](https://github.com/mattheww/gomill)
* [GnuGo](https://www.gnu.org/software/gnugo/)
* [TensorFlow](https://www.tensorflow.org/)
* [GoGui](http://gogui.sourceforge.net/)


## Todo

- [ ] Try additional features such as previous moves, turns since move was
played, color to move next.
- [ ] Try different size model architectures.
- [ ] Compare model with existing score evaluation programs.
- [ ] Optimize the code API and structure.
