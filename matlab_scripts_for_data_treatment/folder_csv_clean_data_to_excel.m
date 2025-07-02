%Processes all data from .csv files in a folder.

clear all
close all

% ---- Enter name of folder path ----
folderPath = input('Enter the path to the folder containing CSV files: ', 's');

% ---- Validate folder ----
if ~isfolder(folderPath)
    error('The folder "%s" does not exist.', folderPath);
end

% ---- Get all .csv files in the folder ----
csvFiles = dir(fullfile(folderPath, '*.csv'));

if isempty(csvFiles)
    error('No CSV files found in the folder.');
end

% ---- Process each CSV file ----
for k = 1:length(csvFiles)
    inputCsvFile = fullfile(folderPath, csvFiles(k).name);
    [~, inputName, ~] = fileparts(inputCsvFile);
    outputExcelFile = fullfile(folderPath, ['ProcessedData_',inputName,'.xlsx']);
    
    fprintf('Processing: %s\n', csvFiles(k).name);
    
    % Open the file
    fid = fopen(inputCsvFile, 'r');
    if fid == -1
        warning('Could not open file: %s. Skipping.', inputCsvFile);
        continue;
    end

    % Read until "DataName"
    lineFound = false;
    lines = {};
    while ~feof(fid)
        currentLine = fgetl(fid);
        if startsWith(currentLine, 'DataName')
            lineFound = true;
            lines{end+1} = currentLine; 
            break;
        end
    end

    % Read rest of the file
    while ~feof(fid)
        currentLine = fgetl(fid);
        lines{end+1} = currentLine; 
    end

    fclose(fid);

    if ~lineFound
        warning('"DataName" not found in %s. Skipping.', csvFiles(k).name);
        continue;
    end

    % Save to temporary CSV
    tempFile = fullfile(folderPath, 'temp_cleaned.csv');
    fid = fopen(tempFile, 'w');
    fprintf(fid, '%s\n', lines{:});
    fclose(fid);

    try
        % Read and clean
        dataTable = readtable(tempFile);
        dataTable(:,1) = [];  % Remove first column

        % Write to Excel
        writetable(dataTable, outputExcelFile, 'Sheet', 'Data');
        fprintf('Saved cleaned file: %s\n', outputExcelFile);
    catch ME
        warning('Error processing %s: %s', csvFiles(k).name, ME.message);
    end

    % Delete temp file
    delete(tempFile);
end

disp('Process complete.');
