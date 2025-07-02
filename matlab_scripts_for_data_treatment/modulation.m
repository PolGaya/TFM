function modulation(scriptName)
    fprintf('Running %s\n', scriptName);

    clear all
    close all
    
    % Enter name of folder path
    folderPath = input('Enter the path to the folder containing .xlsx files: ', 's');
    
    % Validate folder
    if ~isfolder(folderPath)
        error('The folder "%s" does not exist.', folderPath);
    end
    
    fileList = dir(fullfile(folderPath, '*.xlsx'));
    
    % Filter only files with "modulacio" in the name
    modulationFiles = fileList(contains({fileList.name}, '_modulation_'));
    
    if isempty(modulationFiles)
        warning('No file with "_modulation_" in the name was found.');
        return;
    end
    
    % Loop through each matching Excel file
    for fileIdx = 1:length(modulationFiles)
        fileName = modulationFiles(fileIdx).name;
        filePath = fullfile(folderPath, fileName);
     
        % Read data from the Excel file
        data = readmatrix(filePath);
        [~, ~, raw] = xlsread(filePath);
        units = raw(1, :);
        
        % Check if data has at least two columns
        if size(data, 2) < 2
            warning('File %s does not have enough columns to plot.', fileName);
            continue;
        end
    
        % Get X (first column)
        X = data(:, 1);
        dX = diff(X);
    
        % Initialize segments based on step size changes
        segments = {};
        relTol = 1e-5;
        if length(X) < 2
            warning('Not enough X data in %s.', fileName);
            continue;
        end
    
        startIdx = 1;
        prevStep = X(2) - X(1);
    
        for i = 2:length(X)-1
            currentStep = X(i+1) - X(i);
            if abs(currentStep - prevStep) > relTol * abs(prevStep)
                segments{end+1} = startIdx:i;
                startIdx = i + 1;
            end
            prevStep = currentStep;
        end
        segments{end+1} = startIdx:length(X);  % Final segment
    
        fprintf('Processing %s: Found %d segment(s) based on X step size changes.\n', ...
                fileName, length(segments));
    
        % Loop over each Y column (from 2 to end)
        for col = 2:size(data, 2)
            Y = data(:, col);
    
            % Plot all segments on the same figure
            figure;
            hold on;
            for s = 1:length(segments)
                idx = segments{s};
                plot(X(idx), Y(idx), 'LineWidth', 2);
            end
            hold off;
    
            xlabel('Vg1(V)');
            ylabel(sprintf('%s (A)', string(units{col})));
            title(sprintf('Vg1-%s', string(units{col})));
            grid on;
    
            % Save figure
            saveas(gcf, fullfile(folderPath, ...
                sprintf('%s_Col%d_plot.png', fileName(1:end-5), col)));
            close(gcf);
        end
    end
    
    disp('Modulation plots complete.');

end
