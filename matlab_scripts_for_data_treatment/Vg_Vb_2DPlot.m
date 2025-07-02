function Vg_Vb_2DPlot(scriptName)
    fprintf('Running %s\n', scriptName);

    clear all
    close all

    % Prompt user for folder path
    folderPath = input('Enter the path to the folder containing .xlsx files: ', 's');

    % Check folder validity
    if ~isfolder(folderPath)
        error('The folder "%s" does not exist.', folderPath);
    end

    fileList = dir(fullfile(folderPath, '*.xlsx'));

    % Filter files containing "modulation"
    modulation2DFiles = fileList(contains({fileList.name}, '2D'));

    if isempty(modulation2DFiles)
        warning('No file with "2D" in the name was found.');
        return;
    end

    % Loop over matched files
    for fileIdx = 1:length(modulation2DFiles)
        fileName = modulation2DFiles(fileIdx).name;
        filePath = fullfile(folderPath, fileName);

        fprintf('Processing file: %s\n', fileName);

        % Read Vb and Id data from Excel
        data = readmatrix(filePath);

        if size(data, 2) < 2
            warning('File %s does not have at least 2 columns.', fileName);
            continue;
        end

        Vb_full = data(:, 1);
        Id_full = data(:, 2);

        % Extract unique Vb values in order
        [Vb_unique, ~] = unique(Vb_full, 'stable');
        nVb = numel(Vb_unique);

        % Define Vg sweep range (assumption: 101 steps from -2 to 1 V)
        Vg = linspace(-2, 1, 201)';
        nVg = numel(Vg);

        % Consistency check
        if nVb * nVg ~= numel(Id_full)
            warning('Inconsistent data in %s: expected %d Id points, got %d.', ...
                fileName, nVb*nVg, numel(Id_full));
            continue;
        end

        % Reshape Id into a matrix: rows = Vb, cols = Vg
        Id_matrix = reshape(Id_full, nVb, nVg);

        % Prepare grid
        [VB, VG] = meshgrid(Vb_unique, Vg);

        % --- Plot 2D Color Map ---
        figure;
        pcolor(VB, VG, Id_matrix');
        shading interp;
        cb = colorbar;
        cb.Label.String = 'I_D (A)';
        xlabel('V_{b1} = V_{b2} (V)');
        ylabel('V_{Gate} (V)');
        title('Drain-to-source current I_D (A)');
        saveas(gcf, fullfile(folderPath, [fileName(1:end-5), '_ColorMap.png']));
        close(gcf);

        % --- Plot Line Graph at Two Vb Values ---
        Id_VbMin = Id_matrix(1, :);
        Id_VbMax = Id_matrix(end, :);

        figure;
        plot(Vg, Id_VbMax, '-', 'LineWidth', 1.5);
        hold on;
        plot(Vg, Id_VbMin, '--', 'LineWidth', 1.5);
        xlabel('V_g (V)');
        ylabel('I_D (A)');
        title('I_D vs V_G at V_{DS} = 0.250 V');
        legend(sprintf('V_b = %.2f V', Vb_unique(end)), ...
               sprintf('V_b = %.2f V', Vb_unique(1)), ...
               'Location', 'best');
        grid on;
        saveas(gcf, fullfile(folderPath, [fileName(1:end-5), '_VbLinePlot.png']));
        close(gcf);
    end

    disp('VB-VG Modulation plots complete.');
end
