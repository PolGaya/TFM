clear all
close all

% ---- Enter name of folder path ----
folderPath = input('Enter the path to the folder containing .xlsx files: ', 's');

% ---- Validate folder ----
if ~isfolder(folderPath)
    error('The folder "%s" does not exist.', folderPath);
end

fileList = dir(fullfile(folderPath, '*.xlsx'));

% Loop through each Excel file
for fileIdx = 1:length(fileList)
    fileName = fileList(fileIdx).name;
    filePath = fullfile(folderPath, fileName);
    
    % Read data from the Excel file
    data = readmatrix(filePath);
    [~, ~, raw]  = xlsread(filePath);
    units = raw (1, :);
    
    % Check if data has at least two columns
    if size(data, 2) < 2
        warning('File %s does not have enough columns to plot.', fileName);
        continue;
    end
    
    % Get X (first column)
    X = data(:, 1);
    
    % Loop over each Y column (from 2 to end)
    for col = 2:size(data, 2)
        Y = data(:, col);
        
        % Plot
        figure;
        plot(X, Y);
        xlabel(units(1, 1));
        ylabel(sprintf( '%s', string(units{col})));
        title(sprintf('%s', string(units{col}), ' vs ', string(units{1})));
        grid on;
        
        % Save figure
        saveas(gcf, fullfile(folderPath, ...
            sprintf('%s_Col%d.png', fileName(1:end-5), col)));
        close(gcf);
    end
end

disp('Process complete.');