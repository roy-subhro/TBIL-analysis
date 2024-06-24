# -*- coding: utf-8 -*-

class DataExtractor():

    def __init__(self,filename):
        self.file=filename
        with open(self.file,'r') as text:
            self.content=text.read().splitlines()
        self.cycles=self.obtain_cycles()
        self.patient_id=self.obtain_patient_id()
        self.base_data=self.obtain_base_data()
        self.test_data=self.obtain_test_data()
        self.patient_concentration=self.obtain_patient_conc()
        self.device_name=self.obtain_device_name()
        
        
    def obtain_cycles(self):
        import re
        start_indices=[]
        end_indices=[]
        for i,line in enumerate(self.content):
            if re.search("^>>Cycle.* begin<<$",line):
                start_indices.append(i)
            if re.search("^>>Cycle.* end<<$",line):
                end_indices.append(i)
        cycles=[]
        for i in range(len(start_indices)):
            cycles.append(self.content[start_indices[i]+1:end_indices[i]])
        return cycles
    
    def obtain_patient_id(self):
        import re
        patient_id=[]
        for line in self.content:
            if re.search("^Enter Patient",line):
                patient_id.append(line[-4:])
        return patient_id
    def obtain_base_data(self):
        import re
        import numpy as np
        start_indices=[]
        end_indices=[]
        no_of_cycles=len(self.cycles)
        
        base_data=[]
        for j in range(no_of_cycles):
            start_indices=[]
            end_indices=[]
            for i,line in enumerate(self.cycles[j]):
                if re.search("^Take 1000 uL R1",line):
                    start_indices.append(i)
                if re.search("^Insert the cuvette in Slot",line):
                    end_indices.append(i)
                    
            for k in range(len(start_indices)):
                base_data.append({'cycle':j,
                                  'sample_id':self.cycles[j][start_indices[k]][31:35],
                                  'slot_no':  int(self.cycles[j][end_indices[k]][27:29]),
                                  'base_data':np.array([tuple(map(float,data.split(','))) for data in self.cycles[j][start_indices[k]+3:end_indices[k]-3]])
                                  })
        return base_data
    
    
    def obtain_test_data(self):
        import re
        import numpy as np

        no_of_cycles=len(self.cycles)
        test_data=[]
        
        for j in range(no_of_cycles):
            start_indices=[]
            for i,line in enumerate(self.cycles[j]):

                if re.search("^Remove cuvette from slot \d",line) and re.search("into the Device: \[Done\]$",line):
                    start_indices.append(i)
            
            for k in (start_indices):
                data_chunk=[]
                for line in self.cycles[j][k+3:]:
                    if '$' in line:
                        break
                    data_chunk.append(tuple(map(float,line.split(','))))
                test_data.append({'cycle':j,
                                  
                                  'slot_no': int(self.cycles[j][k][25:27]),
                                  'test_data':np.array(data_chunk)
                                  })
        return test_data
    def obtain_patient_conc(self):
        import re
        conc_list=[]
        for line in self.content:
            if re.search("^Patient \d",line):
                conc_list.append(line[-4:])
        return conc_list
    def obtain_device_name(self):
        import re
        for line in self.content[:10]:
            if re.search('^Device ID',line):
                return (line.split(':')[1].strip())
            
            

