# Path Delay Calculator 

A utility that calculates the delay of a path taking into consideration the interconnect effects. The utility accepts a routed
DEF file, the technology LEF and the library liberty file. The user has to specify the path cells in a file.

## Getting Started

The user has to specify the path cells in a file which our utility will read and then give the total delay of the path specified by the user.

### Prerequisites

The user file has to follow a specific format that is specifing the gate/pin an example for this is: 

```
AND2X2_2/A
NAND2X1_7/B
INVX1_10/A 
DFFSR_46/D

```

### How to run this project? ----------------------------



```
Ex

```


End with an example of getting some data out of the system or using it for a little demo

## Running the tests ----------------------------

Explain how to run the automated tests for this system

### Break of the test cases 

There are 11 test cases placed under examples folder. The first 10 cases are valid, yet test case number 11 has a discontinuous path which will create an exception in the validation stage. i.e:

```
The path is discontinuous!

```


## Built With

* [Python](https://www.python.org/) - The language used for developing the project. 
* [PyCharm](https://www.jetbrains.com/pycharm/) - The IDE used for developing the project. 

## Mini Project 

Find our project's code at [GitHub](https://github.com/KhaledSoliman/MiniProjectDigital/issues/created_by/KhaledSoliman)

## Authors

* **Khaled Soliman** - [KhaledSoliman](https://github.com/KhaledSoliman)

* **Mohamed Elsayed** - [MohamedSamirr](https://github.com/MohamedSamirr)

## References 

* [Def Parser](https://github.com/trimcao/lef-parser)  
* [Lef PArser](https://github.com/trimcao/lef-parser)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details ----------------------
