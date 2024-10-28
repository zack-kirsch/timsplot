# timsTOF Visualization Tool
The timsTOF Visualization Tool App is a Shiny App designed to facilitate quick and easy data visualization for Bruker timsTOF data. The app uses the reports from common software (Spectronaut, DIA-NN, FragPipe, and tims DIA-NN) to generate informative figures that can be adjusted on-the-fly for data inspection and presentation. 

# Tutorial
Instructions on how to install and use the app can be found in 'timsTOF Visualization App Tutorial' in the main directory.

# Getting Started
## Installation
1. **Install Python and/or Anaconda:** Make sure you have Python installed on your computer. You can donwload either from their respective websites. (<https://www.python.org/downloads/>, <https://www.anaconda.com/download>)
2. **Install Visual Studio Code:** This will be the primary interface for the app (<https://code.visualstudio.com/>). Make sure to set the Python interpreter in the IDE to the current installed version of Python or Anaconda.
3. **Install required Python libraries:** Most of the libraries needed for the app are built into the installation of Python. The libraries listed below need to be installed manually:

<details>
  
<summary>Python Libraries</summary>

  #### Note: When installing Python libraries, make sure that the installation is under the selected Python interpreter in Visual Studio Code (e.g. if Anaconda is used as the Python interpreter, perform the installations in a Conda powershell prompt).
  #### Each library can be installed in a powershell terminal by typing `pip install {library}`.
  #### Alternatively, make sure the requirements.txt file is in the same directory as the app.py and use `py -m pip install -r requirements.txt` to bulk-install all the nececssary libraries
  - alphatims
  - colorcet
  - faicons
  - hvplot
  - matplotlib-venn
  - scikit-learn
  - shiny
  - shinyswatch
  - upsetplot

</details>

4. **Install required extensions in Visual Studio Code:** In Visual Studio Code, make sure to install the Python and Shiny extensions so the IDE can properly interpret the app file through the Extensions:Marketplace tab.
5. **Download the app from the GitHub repository:** Clone or download the repository containing the app code from the GitHub repository (<https://github.com/zack-kirsch/timsTOF_visualization_tool>).
6. **Run and access the app:** Set the downloaded app directory as the working directory under the Explorer tab in Visual Studio Code and open the app.py file. Click the play button in the top right to launch the Shiny app. If the extensions have been installed properly, you should see `Run Shiny App` when hovering over the button.

## Input File Format
- Spectronaut: Use the report template listed as "Shiny Report Format.rs" to export the search results.
- DIA-NN: The input is the main report .tsv file.
- FragPipe: The input is the psm.tsv result file.
- tims-DIA-NN: To access results file, unzip the bps_timsDIANN folder, open the processing-run folder and its subfolder, then unzip the tims-diann.result folder. Upload the results.tsv file.

# Disclaimer
This application is not supported by or affiliated with Bruker.
