import numpy as np 
import vtk

class PFileClass(object):
    """ properties """        
    """    % constantes   """
    STATUS_OK = 0;
    FILE_ERROR = -1;
    FILENAME_MANDATORY = -2;
    UNSUPPORTED_HEADCOIL = -3;
    UNSUPPORTED_PFILE_VERSION = -4;
    STATUS_NOK = -9;
    EIGHT_CHANNELS = 8;
    SUPPORTED_COILS = {'NORASCPC8ch1', '8HRBRAIN', '8US TORSOPA'};
    """
    DEFAULT_FRAME_RANGE = '[1:end]'; 
    """
    DEFAULT_SEQUENCE_NAME = 'PRESS';

    """    % propiedades """
    """
    central_freq = [];
    cname = [];
    ctr_R = [];
    ctr_A = [];
    ctr_S = []; 
    ex_datetime = [];
    ex_no = [];
    """
    fileName = [];
    frameRange = [];
    """
    magstrength = [];
    mr_flip = [];
    nex = [];
    num_channels = [];
    nwframes = [];
    patid = [];
    patidff = [];
    patname = [];
    patnameff = [];
    ppm_reference = [];
    psdname = [];
    rdb_hdr_ff_data = [];
    rh_frame_size = [];
    rh_point_size = [];
    rh_ps_mps_freq = [];
    rh_raw_pass_size = [];
    rh_rdbm_rev = [];
    rh_user7 = [];
    rh_user19 = [];
    rh_user40 = [];
    roilenx = [];
    roileny = [];
    roilenz = [];
    scan_date = [];
    scan_time = [];
    se_desc = [];
    se_num = [];
    """
    seqName = [];
    """
    sout = [];
    spectral_width = [];
    te = [];
    temperature = [];
    tr = [];
    total_frames_per_coil = [];
    version = [];
    water_frames = [];
    zero_frame = [];      
    """
    """    % constantes derivadas de campos   """
    """
    IS_REV_11_12 = [];
    IS_REV_15 = [];
    """    
    """    % gestion de ficheros   """
    fid = [];
    status = STATUS_OK ;
    """
    """
    """ end %%% properties %%% """
        
    """    methods   """
    def __init__(self):
        self.status = self.STATUS_OK;
    """   end   % Constructor   """


    def info(self):
        attrs = vars(self);
        sortedItems = attrs.items();
        sortedItems.sort();
        return ' '.join("\n%s: %s" % item for item in sortedItems );

    def info(self,node):
        attrs = vtk.vtkStringArray();
        node.GetAttributeNames(attrs);
        sortedItems = [];
        for ix in range(0,attrs.GetNumberOfValues()):
            A = attrs.GetValue(ix);
            sortedItems.append((A,node.GetAttribute(A)));
        sortedItems.sort();        
        return ' '.join("\n%s: %s" % item for item in sortedItems );

    def show(self):
        print self.info();
        
    def openFile(self):
        try:
            self.fid = open(self.fileName,'r');
            if not self.fid:  
               self.status = self.FILE_ERROR;
            else:
               self.status = self.STATUS_OK;        
        except:
               self.status = self.FILE_ERROR;
            
    """ end  %%% OpenFile """
    
    def closeFile(self):
        try:
            self.fid.close();
            self.status = self.STATUS_OK;        
        except:
               self.status = self.FILE_ERROR;
                
    """ end  %%% closeFile """

    def parseFile(self,args):
        if "fileName" in args: 
            self.fileName   = args["fileName"];
        if "seqName" in args: 
            self.seqName    = args["seqName"];
        if "frameRange" in args: 
            self.frameRange = args["frameRange"];        
        if not self.fileName:
            self.status = self.FILENAME_MANDATORY; 
            return self.status;
        if not self.frameRange:
            self.frameRange = "0:";
            
        self.openFile();
        
        if self.status == self.STATUS_OK:
            self.readCommonHeader();
        if self.status == self.STATUS_OK:
            self.readVersionDependentData();   
        if self.status == self.STATUS_OK:
            self.readSignalData(self.frameRange)
            
        if self.status == self.STATUS_OK:
            self.closeFile();  
           
    """  end  %%% parseFile   """
    def readCommonHeader(self): 
        f = self.fid;
        
        self.rh_rdbm_rev = np.fromfile(f,count=1,dtype=np.float32)[0];            # fread(self.fid,1,'float32',0,'l'));

        f.seek(16,0);                                                             # fseek(self.fid, 16, 'bof');                
        self.scan_date = np.fromfile(f,count=10,dtype=np.int8).tostring().split('\x00')[0];        # sprintf('%s',char(transp(fread(self.fid,10,'char',0,'l'))));
 
        f.seek(26,0);                                                             # fseek(self.fid, 26, 'bof');
        self.scan_time = np.fromfile(f,count=8,dtype=np.int8).tostring().split('\x00')[0];         # self.scan_time = sprintf('%s',char(transp(fread(self.fid,8,'char',0,'l'))));

        f.seek(80,0);                                                             # fseek(self.fid, 80, 'bof');
        self.rh_frame_size = int(np.fromfile(f,count=1,dtype=np.uint16)[0]);      # self.rh_frame_size = fread(self.fid,1,'uint16',0,'l');

        f.seek(82,0);                                                             # fseek(self.fid, 82, 'bof');
        self.rh_point_size = int(np.fromfile(f,count=1,dtype=np.uint16)[0]);      # self.rh_point_size =  fread(self.fid,1,'int16',0,'l');

        f.seek(116,0);                                                            # fseek(self.fid, 116, 'bof');
        self.rh_raw_pass_size = int(np.fromfile(f,count=1,dtype=np.int32)[0]);    # self.rh_raw_pass_size = fread(self.fid,1,'int32',0,'l');

        f.seek(244,0);                                                            # fseek(self.fid, 244, 'bof');
        self.rh_user7 = np.fromfile(f,count=1,dtype=np.float32)[0];               # self.rh_user7 =  fread(self.fid,1,'float32',0,'l');

        f.seek(292,0);                                                            # fseek(self.fid, 292, 'bof');
        self.rh_user19 = np.fromfile(f,count=1,dtype=np.float32)[0];              # self.rh_user19 = fread(self.fid,1,'float32',0,'l'); % Probalemente es el no. de reference frames (water)

        f.seek(368,0);                                                            # fseek(self.fid, 368, 'bof');
        self.spectral_width = np.fromfile(f,count=1,dtype=np.float32)[0];         # self.spectral_width = fread(self.fid,1,'float32',0,'l'); 
 
        f.seek(380,0);                                                            # fseek(self.fid, 380, 'bof');
        self.roilenx = np.fromfile(f,count=1,dtype=np.float32)[0];                # self.roilenx = fread(self.fid,1,'float32',0,'l');

        f.seek(384,0);                                                            # fseek(self.fid, 384, 'bof');
        self.roileny = np.fromfile(f,count=1,dtype=np.float32)[0];                # self.roileny = fread(self.fid,1,'float32',0,'l');

        f.seek(388,0);                                                            # fseek(self.fid, 388, 'bof');
        self.roilenz = np.fromfile(f,count=1,dtype=np.float32)[0];                # self.roilenz = fread(self.fid,1,'float32',0,'l');

        f.seek(424,0);                                                            # fseek(self.fid, 424, 'bof');
        self.rh_ps_mps_freq = int(np.fromfile(f,count=1,dtype=np.int32)[0]);      # self.rh_ps_mps_freq =  fread(self.fid,1,'int32',0,'l');

                
        f.seek(1080,0);                                                           # fseek(self.fid, 1080, 'bof');
        self.rh_user40 = np.fromfile(f,count=1,dtype=np.float32)[0];              # self.rh_user40 = fread(self.fid,1,'float32',0,'l'); % Probalemente es el shift del agua (4.7ppm), aparentemente no siempre esta. ojo.

        f.seek(1468,0);                                                           # fseek(self.fid, 1468, 'bof');
        self.rdb_hdr_ff_data= int(np.fromfile(f,count=1,dtype=np.int32)[0]);      # self.rdb_hdr_ff_data =  fread(self.fid,1,'int32',0,'l'); % Punto en el cual comienza la data de espectros

        """
                % campos derivados o constantes
                % Nota: hay un frame que es cero que divide a los grupos de espectros entre bobinas
        """
        self.water_frames = int(self.rh_user19);
        self.zero_frame = 1;             

        self.central_freq = self.rh_ps_mps_freq;
        self.ppm_reference = self.rh_user40;
        self.temperature = self.rh_user7;

        """
                % Por ahora se soporta solo la version 12 y 15
                % Nota: en el codigo original, la version 11 se gestiona como la 12. 
                % Aqui se deja como 11. Cambiar en donde se usa .version    
        """
        self.IS_REV_11_12 = (self.rh_rdbm_rev == 11) or (self.rh_rdbm_rev == 12);
        self.IS_REV_15 = (self.rh_rdbm_rev == 15);
        
        if (self.IS_REV_11_12 or self.IS_REV_15):
            self.version = self.rh_rdbm_rev;
        else:
            self.status = self.UNSUPPORTED_PFILE_VERSION;
        
        """    end  %%% readCommonHeader  """
          
    def readVersionDependentData(self):
        if self.IS_REV_11_12:
            self.readVersion_11_12_Data();
        elif self.IS_REV_15:
            self.readVersion_15_Data();
        
        """
                % campos derivados o constantes
                %
                % El nombre de la bobina si se quiere
                % extender a otras partes del cuerpo, debera controlarse de
                % mejor manera.
                % 
                % Por ejemplo, en .7 de higado el nombre que se leyo fue 
                % "8US TORSOPA"
                % Se Comenta estas instrucciones y se asigna 8 por defecto 
                % Dependera del numero de canales -->
                % incluir esto en archivo de config o revisar mejor el .7
                %
                % No veo de donde sacar que son 8 canales salvo del nombre del
                % dispositivo
        """

        if self.cname in self.SUPPORTED_COILS:
            self.num_channels = self.EIGHT_CHANNELS;
        else:
            self.status = self.UNSUPPORTED_HEADCOIL;
      

        """    end   %%% readVersionDependentData   """
        
    def readVersion_11_12_Data(self):
        f = self.fid;
        
        f.seek(61560,0);                                                                        # fseek(self.fid, 61560, 'bof');
        self.magstrength = int(np.fromfile(f,count=1,dtype=np.int32)[0]);                       # fread(self.fid,1,'int32',0,'l');
        self.magstrength = self.magstrength / 10000.0 ;                                         # %  Gauss to Teslas

        f.seek(61568,0);                                                                        # fseek(self.fid, 61568, 'bof');            
        self.ex_datetime = int(np.fromfile(f,count=1,dtype=np.int32)[0]);                       # fread(self.fid,1,'int32',0,'l');

        f.seek(61576,0);                                                                        # fseek(self.fid, 61576, 'bof');
        self.ex_no = int(np.fromfile(f,count=1,dtype=np.uint16)[0]);                            # fread(self.fid,1,'uint16',0,'l');

        f.seek(61884,0);                                                                        # fseek(self.fid, 61884, 'bof');
        self.patid = np.fromfile(f,count=13,dtype=np.int8).tostring().split('\x00')[0];                          # sprintf('%s',char(transp(fread(self.fid,13,'char',0,'l')))); 
                    
        f.seek(61897,0);                                                                        # fseek(self.fid, 61897, 'bof');
        self.patname = np.fromfile(f,count=25,dtype=np.int8).tostring().split('\x00')[0];                        # sprintf('%s',char(transp(fread(self.fid,25,'char',0,'l'))));

        f.seek(62062,0);                                                                        # fseek(self.fid, 62062, 'bof');
        self.patnameff = np.fromfile(f,count=65,dtype=np.int8).tostring().split('\x00')[0];                      # sprintf('%s',char(transp(fread(self.fid,65,'char',0,'l')))); 

        f.seek(62127,0);                                                                        # fseek(self.fid, 62127, 'bof');
        self.patidff = np.fromfile(f,count=65,dtype=np.int8).tostring().split('\x00')[0];                        # sprintf('%s',char(transp(fread(self.fid,65,'char',0,'l')))); 

        f.seek(62710,0);                                                                        # fseek(self.fid, 62710, 'bof');
        self.se_num = int(np.fromfile(f,count=1,dtype=np.int16)[0]);                            # fread(self.fid,1,'uint16',0,'l');

        f.seek(62786,0);                                                                        # fseek(self.fid, 62786, 'bof');
        self.se_desc = np.fromfile(f,count=65,dtype=np.int8).tostring().split('\x00')[0];                        # sprintf('%s',char(transp(fread(self.fid,65,'char',0,'l'))));  

        f.seek(64564,0);                                                                        # fseek(self.fid, 64564, 'bof');
        self.nex = np.fromfile(f,count=1,dtype=np.float32)[0];                                  # fread(self.fid,1,'float32',0,'l');

        f.seek(64928,0);                                                                        # fseek(self.fid, 64928, 'bof');
        self.ctr_R = np.fromfile(f,count=1,dtype=np.float32)[0];                                # fread(self.fid,1,'float32',0,'l');

        f.seek(64932,0);                                                                        # fseek(self.fid, 64932, 'bof');
        self.ctr_A = np.fromfile(f,count=1,dtype=np.float32)[0];                                # fread(self.fid,1,'float32',0,'l');

        f.seek(64936,0);                                                                        # fseek(self.fid, 64936, 'bof');
        self.ctr_S = np.fromfile(f,count=1,dtype=np.float32)[0];                                # fread(self.fid,1,'float32',0,'l');

        f.seek(65024,0);                                                                        # fseek(self.fid, 65024, 'bof');
        self.tr = int(np.fromfile(f,count=1,dtype=np.int32)[0]);                                #  fread(self.fid,1,'int32',0,'l');
        self.tr = self.tr / 1000.0;                                                             # % usec to msec

        f.seek(65032,0);                                                                        # fseek(self.fid, 65032, 'bof');
        self.te = int(np.fromfile(f,count=1,dtype=np.int32)[0]);                                # fread(self.fid,1,'int32',0,'l');
        self.te = self.te / 1000.0;                                                             # % usec to msec

        f.seek(65244,0);                                                                        # fseek(self.fid, 65244, 'bof');
        self.mr_flip = int(np.fromfile(f,count=1,dtype=np.int16)[0]);                           # fread(self.fid,1,'int16',0,'l');

        f.seek(65374,0);                                                                        # fseek(self.fid, 65374, 'bof');       
        self.psdname = np.fromfile(f,count=33,dtype=np.int8).tostring().split('\x00')[0];                        # sprintf('%s',char(transp(fread(self.fid,33,'char',0,'l')))); 

        f.seek(65420,0);                                                                        # fseek(self.fid, 65420, 'bof');       
        self.seqName = np.fromfile(f,count=16,dtype=np.int8).tostring().split('\x00')[0];                        # sprintf('%s',char(transp(fread(self.fid,16,'char',0,'l')))); 
        
        f.seek(65491);                                                                          # fseek(self.fid, 65491, 'bof');
        self.cname = np.fromfile(f,count=17,dtype=np.int8).tostring().split('\x00')[0];                           # self.cname = sprintf('%s',char(transp(fread(self.fid,17,'char',0,'l'))));

        """    end   %%% readVersion_11_12_Data   """
      
    def readVersion_15_Data(self):
        f = self.fid;
        
        f.seek(140980,0);                                                                        # fseek(self.fid, 140980, 'bof');
        self.magstrength = int(np.fromfile(f,count=1,dtype=np.int32)[0]);                        # fread(self.fid,1,'int32',0,'l');
        self.magstrength = self.magstrength / 10000.0 ;                                          # %% Gauss to Teslas

        f.seek(140988,0);                                                                        # fseek(self.fid, 140988, 'bof');
        self.ex_datetime = int(np.fromfile(f,count=1,dtype=np.int32)[0]);                        # fread(self.fid,1,'int32',0,'l');

        f.seek(141044,0);                                                                        # fseek(self.fid, 141044, 'bof');
        self.ex_no = int(np.fromfile(f,count=1,dtype=np.uint16)[0]);                             # fread(self.fid,1,'uint16',0,'l');

        f.seek(141368,0);                                                                        # fseek(self.fid,141368 , 'bof');
        self.patid = np.fromfile(f,count=13,dtype=np.int8).tostring().split('\x00')[0];                           # sprintf('%s',char(transp(fread(self.fid,13,'char',0,'l')))); 

        f.seek(141381,0);                                                                        # fseek(self.fid,141381 , 'bof');
        self.patname = np.fromfile(f,count=25,dtype=np.int8).tostring().split('\x00')[0];                         # sprintf('%s',char(transp(fread(self.fid,25,'char',0,'l'))));

        f.seek(141546,0);                                                                        # fseek(self.fid,141546 , 'bof');
        self.patnameff = np.fromfile(f,count=65,dtype=np.int8).tostring().split('\x00')[0];                       # sprintf('%s',char(transp(fread(self.fid,65,'char',0,'l')))); 

        f.seek(141611,0);                                                                        # fseek(self.fid,141611 , 'bof');
        self.patidff = np.fromfile(f,count=65,dtype=np.int8).tostring().split('\x00')[0];                         # sprintf('%s',char(transp(fread(self.fid,65,'char',0,'l')))); % quita basuras

        f.seek(142194,0);                                                                        # fseek(self.fid, 142194, 'bof');
        self.se_num = int(np.fromfile(f,count=1,dtype=np.int16)[0]);                             # fread(self.fid,1,'uint16',0,'l');

        f.seek(142318,0);                                                                        # fseek(self.fid, 142318, 'bof');
        self.se_desc = np.fromfile(f,count=65,dtype=np.int8).tostring().split('\x00')[0];                         # sprintf('%s',char(transp(fread(self.fid,65,'char',0,'l')))); % quita basuras 

        f.seek(143952,0);                                                                        # fseek(self.fid, 143952, 'bof');
        self.nex = np.fromfile(f,count=1,dtype=np.float32)[0];                                   # fread(self.fid,1,'float32',0,'l');

        f.seek(144316,0);                                                                        # fseek(self.fid,144316 , 'bof');
        self.ctr_R = np.fromfile(f,count=1,dtype=np.float32)[0];                                 # fread(self.fid,1,'float32',0,'l');

        f.seek(144320,0);                                                                        # fseek(self.fid,144320 , 'bof');
        self.ctr_A = np.fromfile(f,count=1,dtype=np.float32)[0];                                 # fread(self.fid,1,'float32',0,'l');

        f.seek(144324,0);                                                                        # fseek(self.fid,144324 , 'bof');
        self.ctr_S = np.fromfile(f,count=1,dtype=np.float32)[0];                                 # fread(self.fid,1,'float32',0,'l');

        f.seek(144572,0);                                                                        # fseek(self.fid, 144572, 'bof');
        self.tr = int(np.fromfile(f,count=1,dtype=np.int32)[0]);                                 # fread(self.fid,1,'int32',0,'l');
        self.tr = self.tr / 1000.0;                                                              # % usec to msec

        f.seek(144580,0);                                                                        # fseek(self.fid, 144580, 'bof');
        self.te = int(np.fromfile(f,count=1,dtype=np.int32)[0]);                                 # fread(self.fid,1,'int32',0,'l');
        self.te = self.te / 1000.0;                                                              # % usec to msec

        f.seek(144924,0);                                                                        # fseek(self.fid, 144924, 'bof');
        self.mr_flip = int(np.fromfile(f,count=1,dtype=np.int16)[0]);                            # fread(self.fid,1,'int16',0,'l');

        f.seek(145132,0);                                                                        # fseek(self.fid, 145132, 'bof');
        self.psdname = np.fromfile(f,count=33,dtype=np.int8).tostring().split('\x00')[0];                         # sprintf('%s',char(transp(fread(self.fid,33,'char',0,'l')))); 

        f.seek(145178,0);                                                                        # fseek(self.fid, 145178, 'bof');
        self.seqName = np.fromfile(f,count=16,dtype=np.int8).tostring().split('\x00')[0];                         # sprintf('%s',char(transp(fread(self.fid,16,'char',0,'l')))); 

        f.seek(145249,0);                                                                        # fseek(self.fid, 145249, 'bof');
        self.cname = np.fromfile(f,count=17,dtype=np.int8).tostring().split('\x00')[0];                           # sprintf('%s',char(transp(fread(self.fid,17,'char',0,'l'))));
    
        """    end   %%%  readVersion_15_Data """
 
    def readSignalData(self,frameRange):
        f = self.fid;
        
        dt = np.dtype([('1',np.int32),('2',np.int32)])
        f.seek(self.rdb_hdr_ff_data,0);                                                          # fseek(self.fid, self.rdb_hdr_ff_data, 'bof');
        F = np.fromfile(f,count=-1,dtype=dt);                                                    # fread(self.fid,[2,inf],'int32',0,'l');

        self.sout = F['1'] + 1j *  F['2'];                                                       # opcion mas lenta: np.vectorize(complex)(F['1'],F['2']);

        """        
                %%%%%%%% crop de datos
        """
        tt = (self.sout.size/self.rh_frame_size)/self.num_channels;                               # tt =  (size(self.sout,2)/self.rh_frame_size)/self.num_channels; 
        ss = self.sout.reshape(self.rh_frame_size,tt,self.num_channels,order='F').copy();         # reshape(self.sout,[self.rh_frame_size,tt,self.num_channels]);
        self.sout = ss;

        sswz = ss[:, 0:(self.water_frames + self.zero_frame),:];                                  # sswz = ss(:, 1:(self.water_frames + self.zero_frame),:);        
        ss = ss[:, self.water_frames + self.zero_frame:,:];                                       # ss = ss(:, (self.water_frames + self.zero_frame +1):end,:); %#ok<NASGU> 
        """
               NOTA IMPORTANTE: PARA LA IMPLEMENTACION DE PYTHON, LA NOTACION PARA
               DESCRIBIR UN RANGO SERA LA CONVENIDA PARA INDICES EN PYTHON, NO EN MATLAB
               ESTO SUPONE UNA DIFERENCIA CON LA IMPLEMENTACION DE ESTA FUNCION EN MATLAB
               HASTA QUE SE NORMALICE LAS NOTACIONES
        """
        ss = eval('ss[:,' + frameRange + ',:]');                                                  # ss = eval(['ss(:,' frameRange ',:)']);
        self.sout = np.concatenate((sswz,ss),axis=1);                                             # self.sout = [sswz ss];
        ss = [];                                                                                  # ss = []; %#ok<NASGU>
        
        self.sout = self.sout.flatten('F');                                                       # self.sout = transp(self.sout(:));
        
        """        
                % Metadata de senal leida
                % Nota: equivalentemente = no_water_frames + water_frames + zero_frame;
        """
        self.total_frames_per_coil =  (self.sout.size/self.rh_frame_size)/self.num_channels;      # (size(self.sout,2)/self.rh_frame_size)/self.num_channels; 
        self.nwframes = self.total_frames_per_coil - self.water_frames - self.zero_frame;
        
        """ end   %%% readSignalData   """
            
    """ end   %%% classdef PFileClass   """