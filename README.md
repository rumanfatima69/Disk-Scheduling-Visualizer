**_Disk Scheduling Visualizer_**

A Python-based GUI application that visualizes and compares popular disk scheduling algorithms used in Operating Systems. The project helps users understand how disk requests are serviced and how different scheduling strategies affect total head movement.

**Features**
- Interactive graphical user interface built with Tkinter
- Visualization of disk head movement using Matplotlib
- Support for multiple disk scheduling algorithms:
  - FCFS (First Come First Serve)
  - SSTF (Shortest Seek Time First)
  - SCAN
  - C-SCAN
- Displays total head movement
- Shows request servicing sequence
- Generates a cylinder sweep graph for better understandin
  
**Technologies Used**
- Python
- Tkinter
- Matplotlib

**How It Works**
1. Enter disk request values separated by commas.
2. Enter the initial head position.
3. Select a scheduling algorithm.
4. Click Run Algorithm.
5. View the servicing sequence, total movement, and graphical visualization.

   ![image alt](https://github.com/rumanfatima69/Disk-Scheduling-Visualizer/blob/7cfeb6b68622842321cba0c6bf4e7152794e7e29/Interface.png)

   
**Input Validation**

The application validates user input before executing the selected algorithm.

- Requests must be entered as numeric values separated by commas.
- Head position must be a valid integer.
- Empty input fields are not accepted.
  
_- Invalid or non-numeric values will trigger an error message instead of running the algorithm._

**Educational Purpose**
This project was developed as part of learning Operating Systems concepts and provides a visual way to understand disk scheduling techniques and compare their behavior.

**Author**

_Ruman Fatima_

BS Computer Science Student
