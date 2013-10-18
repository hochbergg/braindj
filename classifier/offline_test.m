

% fname = 'recording_Fri Oct 11 14_08_49 2013.bin';
% 
% fid = fopen(fname);
% A = fread(fid, inf, 'int32');
% fclose(fid);
% 
clear
close all
 

% fname = 'recording_Fri Oct 11 14_08_49 2013.csv';
fname = 'EEGdata2.csv'
refch = 5;
rawdata = csvread(fname);


%% preprocessing

rec = rawdata(:,3:end);
songidx = rawdata(:,1);
labels_cont = rawdata(:,2);
labels = labels_cont >=2;

% %%%% GENERATING SYNTHETIC DATA
% rec = repmat(rec,30,1);
% songidx = repmat([1:10] , length(rec)/10 ,1); songidx=songidx(:);
% scoresidx = rand(1,10) > 0.5;
% labels = scoresidx(songidx);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



refv = rec(:,refch);
rec = rec - repmat(refv,1,size(rec,2));
rec(:,refch)=[];
rec = rec - mean(mean(rec));
% for ch=1:size(rec,2)
% rec(:,ch) = rec(:,ch)/std(rec(:,ch));
% end

rec = rec/std(rec(:));

%%
dt = 2; %msec
Twin = 10000; %msec
nsmpwin = floor(Twin/dt);
df = 1/(nsmpwin*dt*1e-3);
fmax = 25; %Hz
fmaxidx = floor(25/df);
fminidx = floor(2/df);
nsmp = size(rec,1);
winnum = floor(nsmp/nsmpwin);
nsmpmax = winnum*nsmpwin;

labels_decim = labels(10:nsmpwin:end); % these are the labels for the training classifier
labels_decim(end) = [];

chRange = [1:7];
NCH = numel(chRange); % number of channels (electrodes)
FTdata = zeros((length((fminidx:fmaxidx))-1)*length((0:winnum-1)), NCH);
for ch=chRange
    v = rec(1:nsmpmax,ch);
%      vs = (1:nsmpmax); % THIS LINE IS FOR DEBUGGING ONLY
    
    v= v-mean(v);
    rv = reshape(v,nsmpwin,winnum); % work on non-overlap windows of the data
    
    Frv = abs(fft(rv)).^2; % 
    Frv((fmaxidx+1):end,:) = []; % trim all non important freqs
    Frv(1:fminidx,:) = [];
    FTdata(:,ch) = Frv(:);
%     maxpower = max(max(Frv));
    
    imagesc((0:winnum-1)*(Twin*1e-3), (fminidx:fmaxidx)*df, (Frv))
    xlabel ('time win [sec]');
    ylabel ('freq [Hz]'); colorbar;
end
%%

merged_channels_FTdata = reshape(FTdata.', numel(FTdata)/winnum,winnum);

%% 
load('model.mat');

svmpredict(double(labels_decim), merged_channels_FTdata.',mymodel);
% 
% clear overfitting
% clear pred
% labels_decim = 2*double(labels_decim)-1;
% rng(0); % random seed
% five_folds_selection = floor(rand(winnum,1)*5)+1;
% [model, predict_label, accuracy, prob_estimates] = deal(cell(5,1));
% 
% cnt = 1;
% grange = 0.1:0.5:5;
% crange = 0.1:0.5:5;
% grange = 1;
% crange = 4;
% 
% x =1;
% y=1;
% for c = crange
%      y=1;
%     for g = grange
%        
%         for k=1:5
%             test_data = merged_channels_FTdata(:,five_folds_selection==k).';
%             test_labels = labels_decim(five_folds_selection==k);
%             train_data = merged_channels_FTdata(:,five_folds_selection~=k).';
%             train_labels = labels_decim(five_folds_selection~=k);
%             % keyboard
%             model{k} = svmtrain(train_labels, train_data,['-g ' num2str(g) ' -c ' num2str(c)]);
%             [predict_label{k}, accuracy{k}, prob_estimates{k}] = svmpredict(train_labels, train_data, model{k});
%             %         pred(cnt) = sum(predict_label{k});
%             overfitting(x,y) = sum(predict_label{k} == train_labels)/length(train_labels);
%             
%             % keyboard
%             [predict_label{k}, accuracy{k}, prob_estimates{k}] = svmpredict(test_labels, test_data, model{k});
%             pred(x,y) = sum(predict_label{k} == test_labels)/length(test_labels);
%             % figure
%             auc(x,y)= myauc(logical(test_labels+1),  prob_estimates{k}, false);
%             y = y+1;
%         end
%         x=x+1;
%         
%     end
% end
% figure
% imagesc(crange, grange, overfitting);%, range, pred); shg
% figure
% imagesc(crange, grange, pred);
% figure
% imagesc(crange, grange, auc);
% % model = svmtrain(heart_scale_label, heart_scale_inst, '-c 1 -g 0.07 -b 1');
% % [predict_label, accuracy, prob_estimates] = svmpredict(heart_scale_label, heart_scale_inst, model, '-b 1');
% % model = svmtrain(training_label_vector, training_instance_matrix [, 'libsvm_options']);
% % 
% %         -training_label_vector:
% %             An m by 1 vector of training labels (type must be double).
% %         -training_instance_matrix:
% %             An m by n matrix of m training instances with n features.
% %             It can be dense or sparse (type must be double).
% %         -libsvm_options:
% %             A string of training options in the same format as that of LIBSVM.
