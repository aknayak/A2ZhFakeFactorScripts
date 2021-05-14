#include <iostream>
#include <math.h>
#include <stdlib.h>
#include <fstream>
#include <iomanip>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <algorithm> // std::max
#include <sys/types.h>
#include <sys/stat.h>

/* 
Run instructions
root -l -b 
.L makeFakeRateDataCard.C
makeFakeRateDataCards()
*/

// lepType: e, mu
// region: pass, fail

void makeFakeRateDataCard(string lepType, string region, string ptbin, string etabin)
{

  //create datacard directory, if not exists
  if (mkdir("datacards", S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH) == -1)
    {
      if( errno == EEXIST ) {
	// alredy exists 
      } else {
        // something else
	std::cout << "cannot create directory datacards, error:" << strerror(errno) << std::endl;
        throw std::runtime_error( strerror(errno) );
      }
    }
  TString outFile(Form("datacards/shapes_%s_%s_%s_%s.root", lepType.c_str(), region.c_str(), ptbin.c_str(), etabin.c_str()));
  TFile* fout = new TFile(outFile, "RECREATE");

  TString inputFilePath("./mt_plots/");
  //Fill DY
  TFile* fDY = TFile::Open(inputFilePath+"plots_DYJetsToLL_M-50.root", "READ");
  if(fDY == 0) return;
  if(fDY->IsZombie()){fDY->Close(); return;}

  fout->cd();
  TH1F* prompt_DY = (TH1F*)(fDY->Get(("mt_"+lepType+"_"+region+"_"+ptbin+"_"+etabin+"_prompt").c_str()))->Clone("prompt");
  //prompt_DY->SetName("prompt");
  //prompt->Write("prompt");
  TH1F* prompt = (TH1F*)prompt_DY->Clone();
  prompt->SetName("prompt");                                                                                                                       

  TH1F* fake_DY = (TH1F*)(fDY->Get(("mt_"+lepType+"_"+region+"_"+ptbin+"_"+etabin+"_fake").c_str()))->Clone("fake");
  //fake->SetName("fake");
  //fake->Write("fake");
  TH1F* fake = (TH1F*)fake_DY->Clone();
  fake->SetName("fake"); 
  fDY->Close();

  //Fill TTBar
  TFile* ftt = TFile::Open(inputFilePath+"plots_TTbar.root", "READ");
  if(ftt == 0) return;
  if(ftt->IsZombie()){ftt->Close(); return;}

  TH1F* prompt_tt = (TH1F*)(ftt->Get(("mt_"+lepType+"_"+region+"_"+ptbin+"_"+etabin+"_prompt").c_str()))->Clone("prompt");
  prompt->Add(prompt_tt);

  TH1F* fake_tt = (TH1F*)(ftt->Get(("mt_"+lepType+"_"+region+"_"+ptbin+"_"+etabin+"_fake").c_str()))->Clone("fake");
  fake->Add(fake_tt);
  ftt->Close();
  
  //Fill VV
  TFile* fvv = TFile::Open(inputFilePath+"plots_Diboson.root", "READ");
  if(fvv == 0) return;
  if(fvv->IsZombie()){fvv->Close(); return;}

  TH1F* prompt_vv = (TH1F*)(fvv->Get(("mt_"+lepType+"_"+region+"_"+ptbin+"_"+etabin+"_prompt").c_str()))->Clone("prompt");
  prompt->Add(prompt_vv);

  TH1F* fake_vv = (TH1F*)(fvv->Get(("mt_"+lepType+"_"+region+"_"+ptbin+"_"+etabin+"_fake").c_str()))->Clone("fake");
  fake->Add(fake_vv);
  fvv->Close();
  fout->cd();
  prompt->Write();
  fake->Write();

  //Fill Data
  TFile* fdata = TFile::Open(inputFilePath+"plots_data.root", "READ");
  if(fdata == 0) return;
  if(fdata->IsZombie()){fdata->Close(); return;}

  TH1F* data = (TH1F*)(fdata->Get(("mt_"+lepType+"_"+region+"_"+ptbin+"_"+etabin+"_data").c_str()))->Clone("data");
  data->SetName("data_obs");
  fout->cd();
  data->Write("data_obs");

  //Make Data card for each bins
  ifstream in;
  char* c = new char[1000];
  in.open("template/datacard_fit_template.txt");


  //create new datacard.txt files
  ofstream out(Form("datacards/datacard_fit_%s_%s_%s_%s.txt", lepType.c_str(), region.c_str(), ptbin.c_str(), etabin.c_str()));
  out.precision(8);

  time_t secs=time(0);
  tm *t=localtime(&secs);
  
  while (in.good())
    {
      in.getline(c,1000,'\n');
      if (in.good()){
	string line(c);
          
	if(line.find("Date")!=string::npos){
	  string day = string(Form("%d",t->tm_mday));
	  string month = string(Form("%d",t->tm_mon+1));
	  string year = string(Form("%d",t->tm_year+1900));
	  line.replace( line.find("XXX") , 3 , day+"/"+month+"/"+year);
	  out << line << endl;
	}
	else if(line.find("shapes")!=string::npos){
	  line.replace( line.find("XXX") , 3 , string(Form("datacards/shapes_%s_%s_%s_%s", lepType.c_str(), region.c_str(), ptbin.c_str(), etabin.c_str()))  );
	  out << line << endl;
	}
	else if(line.find("Observation")!=string::npos){
	  line.replace( line.find("XXX") , 3 , string(Form("%.0f", data->Integral()) )  );
	  out << line << endl;
	}
	else if(line.find("rate")!=string::npos && line.find("rateParam")==string::npos){
	  string rate = "rate      ";  
	  string space = "      ";
	  out << rate ;
	  out << space << fake->Integral()
	      << space << prompt->Integral()
	      << space <<endl;
	}
	else if(line.find("CMS_norm_fake")!=string::npos){
	  line.replace( line.find("XXXX") , 4 , string(Form("%.2f", 1.10)) ); 
	  out << line << endl;
	}
	else if(line.find("CMS_norm_prompt")!=string::npos){
          line.replace( line.find("XXXX") , 4 , string(Form("%.2f", 1.10)) );
          out << line << endl;
	}
	else{
	  out << c << endl;
	}
      }
    }
        
  out.close();
  in.close();
  fout->Close();
}

void makeFakeRateDataCards()
{
  makeFakeRateDataCard("muon", "pass", "Pt10To20", "barrel");
  makeFakeRateDataCard("muon", "pass", "Pt10To20", "endcap");
  makeFakeRateDataCard("muon", "fail", "Pt10To20", "barrel");
  makeFakeRateDataCard("muon", "fail", "Pt10To20", "endcap");
  makeFakeRateDataCard("muon", "pass", "Pt20To30", "barrel");
  makeFakeRateDataCard("muon", "pass", "Pt20To30", "endcap");
  makeFakeRateDataCard("muon", "fail", "Pt20To30", "barrel");
  makeFakeRateDataCard("muon", "fail", "Pt20To30", "endcap");
  makeFakeRateDataCard("muon", "pass", "Pt30To40", "barrel");
  makeFakeRateDataCard("muon", "pass", "Pt30To40", "endcap");
  makeFakeRateDataCard("muon", "fail", "Pt30To40", "barrel");
  makeFakeRateDataCard("muon", "fail", "Pt30To40", "endcap");
  makeFakeRateDataCard("muon", "pass", "Pt40To60", "barrel");
  makeFakeRateDataCard("muon", "pass", "Pt40To60", "endcap");
  makeFakeRateDataCard("muon", "fail", "Pt40To60", "barrel");
  makeFakeRateDataCard("muon", "fail", "Pt40To60", "endcap");

  gApplication->Terminate();
}
  
