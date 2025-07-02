function B1G1(scriptName)
    fprintf('Running %s\n', scriptName);

    close all
    
    % Enter name of folder path 
    folderPath = input('Enter the path to the folder containing .xlsx files: ', 's');
    
    % Validate folder 
    if ~isfolder(folderPath)
        error('The folder "%s" does not exist.', folderPath);
    end
    
    fileList = dir(fullfile(folderPath, '*.xlsx'));
    
    % Filter only files with "B1G1" in the name
    b1g1Files = fileList(contains({fileList.name}, 'B1G1'));
    
    if isempty(b1g1Files)
        warning('No file with "B1G1" in the name was found.');
        return;
    end
    
    % Loop through each matching Excel file
    for fileIdx = 1:length(b1g1Files)
        fileName = b1g1Files(fileIdx).name;
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
        % Check that we have at least three columns for X, Y1, Y3
        if size(data, 2) < 3
            warning('File %s does not have enough columns (at least 3) to plot X, Y1, and Y3.', fileName);
            continue;
        end
    
        Y1 = data(:, 2);
        Y2 = data(:, 3);
    
        % Plot both Y1 and Y2 against X on the same figure
        figure;
        hold on;
        for s = 1:length(segments)
            idx = segments{s};
            plot(X(idx), Y1(idx), 'b-', 'LineWidth', 2); % Blue for Y1
            plot(X(idx), Y2(idx), 'r-', 'LineWidth', 2); % Red dashed for Y3
        end
        hold off;
    
        xlabel('V_ b-g(V)');
        ylabel('I(A)');
        title('B_1-G_1');
        legend('I_ (barrier1)', 'I_ (gate1)');
        grid on;
    
        % Save figure
        saveas(gcf, fullfile(folderPath, ...
            sprintf('%s_plot.png', fileName(1:end-5))));
        close(gcf);
    
    end
    
    disp('B1G1 plot complete.');
    
end