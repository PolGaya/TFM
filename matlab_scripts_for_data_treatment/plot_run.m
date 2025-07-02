% controller_script.m
clear; clc; close all;

% List of function handles instead of script names
scriptsToRun = {
    @() BTBT('BTBT.m')
    @() B1B2('B1B2.m')
    @() G1G2('G1G2.m')
    @() B1G1('B1G1.m')
    @() B2G2('B2G2.m')
    @() Dactivation('Dactivation.m')
    @() Sactivation('Sactivation.m')
    @() Spostactivation('Spostactivation.m')
    @() Dpostactivation('Dpostactivation.m')
    @() modulationG1('modulationG1.m')
    @() modulationG2('modulationG2.m')
    @() modulation('modulation.m')
    @() Vg_Vb_2DPlot('Vg_Vb_2DPlot.m')
    @() SD('SD.m')
};

% Run each script (now functions)
for i = 1:length(scriptsToRun)
    try
        scriptsToRun{i}();
    catch ME
        warning('Failed to run script #%d. Error:\n%s', i, ME.message);
    end
end

disp('All scripts executed.');
