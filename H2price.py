from PIL import Image
Image.CUBIC = Image.BICUBIC
import ttkbootstrap as ttk
import tkinter as tk
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


current_date=pd.to_datetime("today").normalize()
init_date=pd.to_datetime("2023-03-31")
date_30=current_date-pd.Timedelta(30,unit='D')


class Main():
    def __init__(self):
        #CREATE ROOT WINDOW
        self.width=550
        self.height=620
        self.root=ttk.Window(themename='darkly')
        self.window_spec(self.root,self.width,self.height,"H2price")
        self.root.lift() #Keep window on top
        self.root.protocol("WM_DELETE_WINDOW",self.exit)
        
        #LOAD IMAGES
        self.img_bgmain=ttk.PhotoImage(file="Images/bgmain.png")
        self.img_btndetails=ttk.PhotoImage(file="Images/btndetails.png")

        #MENU BAR
        menu=ttk.Menu(self.root)
        self.root.config(menu=menu)
        admin_menu=ttk.Menu(menu)
        menu.add_cascade(label="Admin",menu=admin_menu)
        admin_menu.add_command(label="Cena energii",command=lambda:self.admin_window("energii"))
        admin_menu.add_command(label="Cena wody",command=lambda:self.admin_window("wody"))
        admin_menu.add_command(label="Obowiązująca cena H2",command=lambda:self.admin_window("H2"))

        #CREATE CANVAS
        self.canvas=ttk.Canvas(self.root,width=self.width,height=self.height)
        self.canvas.pack(fill=ttk.BOTH,expand=True)
        self.canvas.create_image(0,0,image=self.img_bgmain,anchor=ttk.NW)
        
        #WIDGETS
        prices_df=read_data[1]
        prices_30=read_data[2]
        H2_price=prices_df.iloc[-1,4]
        
        date_Lab=self.canvas.create_text(460,70,text=f"{current_date.strftime('%d.%m.%Y')} r.",fill="white",justify=ttk.CENTER,font=("Purisa",13,"bold"))
        
        self.energy_price_Lab=self.canvas.create_text(193,132,text=prices_df.iloc[-1,3],fill="white",justify=ttk.CENTER,font=("Purisa",16,"bold"))
        self.ON_price_Lab=self.canvas.create_text(132,215,text=prices_df.iloc[-1,1],fill="white",justify=ttk.CENTER,font=("Purisa",16,"bold"))
        self.water_price_Lab=self.canvas.create_text(194,295,text=prices_df.iloc[-1,2],fill="white",justify=ttk.CENTER,font=("Purisa",16,"bold"))
        
        indicator=self.indicator(H2_price,prices_30)
        self.H2_price_Meter=ttk.Meter(bootstyle=indicator[1],amounttotal=indicator[0],amountused=H2_price,amountformat="{:.2f}",textfont='-size 24 -weight bold',metersize=156,subtext="zł/kg",stripethickness=5)
        H2_price_Meter_c=self.canvas.create_window(276,139,anchor=ttk.NW,window=self.H2_price_Meter)

        self.H2min_price_Lab=self.canvas.create_text(280,387,text=prices_30[0],fill="white",justify=ttk.CENTER,font=("Purisa",13))
        self.H2avg_price_Lab=self.canvas.create_text(343,387,text=prices_30[1],fill="white",justify=ttk.CENTER,font=("Purisa",13))
        self.H2max_price_Lab=self.canvas.create_text(405,387,text=prices_30[2],fill="white",justify=ttk.CENTER,font=("Purisa",13))

        details_Btn=tk.Button(self.root,image=self.img_btndetails,highlightthickness=0,command=self.details_btn)
        details_Btn_c=self.canvas.create_window(479,375,anchor=ttk.NW,window=details_Btn)

        #PLOT
        self.fig=plt.figure(figsize=(5.5,1.85),facecolor="#050505")
        self.fig.subplots_adjust(top=1,right=0.97,left=0.03,bottom=0.22)

        self.ax=self.fig.add_subplot(1,1,1,facecolor="#050505")  
        self.ax.spines[["left","right","top"]].set_visible(False)
        self.ax.spines["bottom"].set_color("#403f3f")
        
        self.update_plot(prices_df,prices_30)

        canvas_plt=FigureCanvasTkAgg(self.fig,self.root)
        canvas_plt.get_tk_widget()
        canvas_plt_c=self.canvas.create_window(0,415,anchor=ttk.NW,window=canvas_plt.get_tk_widget())


    def window_spec(self,parent,width,height,bar_label):
        parent.attributes("-alpha",0)
        
        parent.title(bar_label)
        parent.iconbitmap("Images/logo.ico")
        
        #Resize window and centering it
        screen_width=parent.winfo_screenwidth()
        screen_height=parent.winfo_screenheight()
        x=int((screen_width/2)-(width/2))
        y=int((screen_height/2)-(height/1.82))
        parent.geometry(f"{width}x{height}+{x}+{y}")
        parent.resizable(0,0)

        parent.attributes("-alpha",1) #Hide a temporary window that displays in random places during launching main window


    def indicator(self,H2_price,prices_30): #Handle indicator in Meter widget
        if H2_price == prices_30[2]:
            index_Meter=0
            amounttotal_Meter=H2_price*100
        elif H2_price > prices_30[1]:
            index_Meter=1-((H2_price-prices_30[1])/(prices_30[2]-prices_30[1])/2+0.5)
            amounttotal_Meter=H2_price/index_Meter    
        else:
            index_Meter=1-((H2_price-prices_30[1])/(prices_30[1]-prices_30[0])/2+0.5)
            amounttotal_Meter=H2_price/index_Meter

        if index_Meter > 0.75:
            indicator_style="success"
        elif index_Meter < 0.25:
            indicator_style="danger"
        else:
            indicator_style="info"
            
        return amounttotal_Meter, indicator_style


    def update_plot(self,prices_df,prices_30):
        x_arg=prices_df.loc[prices_df["Data"]>=date_30,"Data"]
        y_arg=prices_df.loc[prices_df["Data"]>=date_30,"H2"]

        self.ax.clear()
        
        self.ax.fill_between(x=x_arg,y2=y_arg,y1=prices_30[0],color="#0E4A92",alpha=0.15)
        self.ax.plot(x_arg,y_arg,color="#0E4A92")
        self.ax.tick_params(left=False,labelleft=False,color="#403f3f",labelcolor="#AEADAD",labelrotation=30,labelsize=9)
        self.ax.margins(x=0,y=0.03)

        self.ax.xaxis.set_major_locator(ticker.LinearLocator(numticks=16))
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))

        self.fig.canvas.draw()


    def admin_window(self,name): #Panel placed in menu bar that provides manual update of price data
        self.window=ttk.Toplevel(self.root)
        self.window_spec(self.window,200,200,f"Cena {name}")
        self.window.grab_set()
        
        price_Lab=ttk.Label(self.window,text=f"Cena {name}:")
        price_Ent=ttk.Entry(self.window,width=20)
        price_Lab.place(x=33,y=10)
        price_Ent.place(x=33,y=30)

        date_Lab=ttk.Label(self.window,text="Data obowiązywania:")
        date_Ent=ttk.DateEntry(self.window,width=15,bootstyle="dark",dateformat="%Y-%m-%d")
        date_Lab.place(x=33,y=70)
        date_Ent.place(x=33,y=90)

        update_Btn=ttk.Button(self.window,text="Zmień",width=7,bootstyle="primary",command=lambda:self.update_btn(name,price_Ent,date_Ent))
        update_Btn.place(x=65,y=145)


    def update_btn(self,name,price,date): #Handle button placed in admin window
        global read_data
    
        prices_df=read_data[1]

        if name == "wody":
            prices_df=data.update(date.entry.get(),water_price=price.get().replace(",","."),last_prices_df=prices_df)
            data.write_db(prices_df)
            self.update_widgets(name,prices_df)
        elif name == "energii":
            prices_df=data.update(date.entry.get(),energy_price=price.get().replace(",","."),last_prices_df=prices_df)
            data.write_db(prices_df)
            self.update_widgets(name,prices_df)
        elif name == "H2":
            H2contr_df=read_data[3]
            H2contr_df=pd.concat([H2contr_df,prices_df.loc[prices_df["Data"]==date.entry.get()]],ignore_index=True)
            H2contr_df.sort_values("Data",inplace=True,ignore_index=True)
            data.write_db(H2contr_df=H2contr_df)

        #Update global data
        read_data=data.read_db()
            
        #Close admin window
        self.window.destroy()


    def update_widgets(self,name,prices_df): #This method is used in case of manual update of prices in admin panel
        prices_30=data.prices_30(prices_df)
        H2_price=prices_df.iloc[-1,4]
        
        #Update Label widget
        if name == "wody":
            self.canvas.itemconfig(self.water_price_Lab,text=prices_df.iloc[-1,2])
        elif name == "energii":
            self.canvas.itemconfig(self.energy_price_Lab,text=prices_df.iloc[-1,3])

        #Update Meter widget
        indicator=self.indicator(H2_price,prices_30)
        self.H2_price_Meter.configure(bootstyle=indicator[1],amounttotal=indicator[0],amountused=H2_price)

        #Update H2_30 label widgets
        self.canvas.itemconfig(self.H2min_price_Lab,text=prices_30[0])
        self.canvas.itemconfig(self.H2avg_price_Lab,text=prices_30[1])
        self.canvas.itemconfig(self.H2max_price_Lab,text=prices_30[2])

        #Update plot
        self.update_plot(prices_df,prices_30)


    def details_btn(self): #Open window with details
        details=Details(self.root)


    def exit(self): #Handle "clean" exit from program 
        self.root.quit() #Break backround process on PC
        self.root.destroy()




class Details(Main):
    def __init__(self,parent):
        self.parent=parent
        self.parent.withdraw() #Hide parent window

        #CREATE TOPLEVEL WINDOW
        self.width=1400
        self.height=700
        self.window=ttk.Toplevel(self.parent)
        self.window_spec(self.window,self.width,self.height,"H2price")
        self.window.focus_force()#force focus to be able scroll historical prices table without having to click a window
        self.window.protocol("WM_DELETE_WINDOW",main.exit)

        #CREATE CANVAS
        self.canvas=ttk.Canvas(self.window,width=self.width,height=self.height)
        self.canvas.pack(fill=ttk.BOTH,expand=True)
        self.canvas.img_bgdetails=ttk.PhotoImage(file="Images/bgdetails.png")
        self.canvas.create_image(0,0,image=self.canvas.img_bgdetails,anchor=ttk.NW)
        
        #WIDGETS
        prices_df=read_data[1]
        H2contr_df=read_data[3]

        self.img_btnreturn=ttk.PhotoImage(file="Images/btnreturn.png")
        return_Btn=tk.Button(self.window,image=self.img_btnreturn,highlightthickness=0,command=self.return_btn)
        return_Btn_c=self.canvas.create_window(45,40,anchor=ttk.NW,window=return_Btn)

        #Current prices section
        H2_current_Lab=self.canvas.create_text(280,66,text=prices_df.iloc[-1,4],fill="#BC8E19",justify=ttk.CENTER,font=("Purisa",22,"bold"))
        date_current_Lab=self.canvas.create_text(290,100,text=prices_df.iloc[-1,0].strftime('%d.%m.%Y'),fill="white",justify=ttk.CENTER,font=("Purisa",13))
        energy_current_Lab=self.canvas.create_text(463,36,text=prices_df.iloc[-1,3],fill="white",justify=ttk.CENTER,font=("Purisa",13))
        ON_current_Lab=self.canvas.create_text(463,67,text=prices_df.iloc[-1,1],fill="white",justify=ttk.CENTER,font=("Purisa",13))
        water_current_Lab=self.canvas.create_text(463,98,text=prices_df.iloc[-1,2],fill="white",justify=ttk.CENTER,font=("Purisa",13))

        #Contract prices section
        H2_contract_Lab=self.canvas.create_text(670,66,text=H2contr_df.iloc[-1,4],fill="#BC8E19",justify=ttk.CENTER,font=("Purisa",22,"bold"))
        date_contract_Lab=self.canvas.create_text(675,100,text=H2contr_df.iloc[-1,0].strftime('%d.%m.%Y'),fill="white",justify=ttk.CENTER,font=("Purisa",13))
        energy_contract_Lab=self.canvas.create_text(851,36,text=H2contr_df.iloc[-1,3],fill="white",justify=ttk.CENTER,font=("Purisa",13))
        ON_contract_Lab=self.canvas.create_text(851,67,text=H2contr_df.iloc[-1,1],fill="white",justify=ttk.CENTER,font=("Purisa",13))
        water_contract_Lab=self.canvas.create_text(851,98,text=H2contr_df.iloc[-1,2],fill="white",justify=ttk.CENTER,font=("Purisa",13))

        #Filter section - combobox
        filter_list=["TYDZIEŃ","MIESIĄC","ROK","WSZYSTKO"]
        self.filter_Cbx=ttk.Combobox(self.window,values=filter_list,width=11,state="readonly",font=("Purisa",10,"bold"),bootstyle="dark")
        self.filter_Cbx.current(3)
        filter_Cbx_c=self.canvas.create_window(35,165,anchor=ttk.NW,window=self.filter_Cbx)
        self.filter_Cbx.bind("<<ComboboxSelected>>",lambda x:self.filter(prices_df))

        #Filter section - prices 
        self.H2min_Lab=self.canvas.create_text(280,178,fill="#4EB0E7",justify=ttk.CENTER,font=("Purisa",22,"bold"))
        self.H2min_date_Lab=self.canvas.create_text(287,210,fill="white",justify=ttk.CENTER,font=("Purisa",13))

        self.H2avg_Lab=self.canvas.create_text(540,178,fill="#4EB0E7",justify=ttk.CENTER,font=("Purisa",22,"bold"))
        self.H2avg_info_Lab=self.canvas.create_text(555,210,fill="white",justify=ttk.CENTER,font=("Purisa",13))

        self.H2max_Lab=self.canvas.create_text(808,178,fill="#4EB0E7",justify=ttk.CENTER,font=("Purisa",22,"bold"))
        self.H2max_date_Lab=self.canvas.create_text(820,210,fill="white",justify=ttk.CENTER,font=("Purisa",13))

        #Filter section - plot
        self.plot_Lab=self.canvas.create_text(542,250,fill="white",justify=ttk.CENTER,font=("Purisa",13))
        
        self.fig=plt.figure(figsize=(8.95,4.15),facecolor="#222222")
        self.fig.subplots_adjust(top=0.97,right=0.967,left=0.06,bottom=0.1)

        self.ax=self.fig.add_subplot(1,1,1,facecolor="#222222")  
        self.ax.spines[["left","right","top","bottom"]].set_color("#403f3f")
        
        canvas_plt=FigureCanvasTkAgg(self.fig,self.window)
        canvas_plt.get_tk_widget()
        canvas_plt_c=self.canvas.create_window(28,260,anchor=ttk.NW,window=canvas_plt.get_tk_widget())
        
        #Filter section - update
        self.filter(prices_df)

        #Historical prices section - treeview table
        style=ttk.Style()
        style.configure("Treeview",font=("Purisa",12))
        style.configure("Treeview.Heading",font=("Purisa",12))

        y_scrollbar=ttk.Scrollbar(self.window,orient=tk.VERTICAL)
        self.tree=ttk.Treeview(self.window,columns=data.cols,height=39,yscrollcommand=y_scrollbar.set)
        y_scrollbar.config(command=self.tree.yview)
        
        tree_canvas=self.canvas.create_window(976,50,anchor=tk.NW,window=self.tree)
        y_scrollbar_canvas=self.canvas.create_window(1350,50,anchor=tk.NW,window=y_scrollbar,heigh=621)

        for col in data.cols:
            self.tree.heading(col,text=col,command=lambda _col=col: self.treeview_sort_column(self.tree,_col,True))
            
        [self.tree.column(f'#{i}',width=90,anchor=ttk.CENTER) if i==1 else self.tree.column(f'#{i}',width=70,anchor=ttk.CENTER) for i in range(6)]

        tv_prices_df=prices_df.sort_values("Data",ascending=False)
        
        for index, row in tv_prices_df.iterrows():
            self.tree.insert("", 'end', text=index, values=list(row))

        self.tree.bind("<Button-1>",self.tv_lock_cols_resizing) #Prevent from manual resizing of columns
        self.tree["show"]="headings" #Hide first column with index


    def tv_lock_cols_resizing(self,event):
        if self.tree.identify_region(event.x,event.y) == "separator":
           return "break"


    def filter(self,prices_df):
        filter_status=self.filter_Cbx.get()
        numticks=16
        rotation=20
        
        if filter_status == "TYDZIEŃ":
            start_date=current_date-pd.Timedelta(7,unit='D')
            numticks=8
            rotation=0
        elif filter_status == "MIESIĄC":
            start_date=current_date-pd.Timedelta(30,unit='D')
        elif filter_status == "ROK":
            start_date=current_date-pd.Timedelta(365,unit='D')
        elif filter_status == "WSZYSTKO":
            start_date=init_date+pd.Timedelta(1,unit='D')

        H2prices_filter=prices_df.loc[prices_df["Data"]>=start_date,["Data","H2"]]

        H2min=H2prices_filter["H2"].min()
        H2min_date=H2prices_filter.loc[H2prices_filter["H2"]==H2min,"Data"].iloc[-1].strftime("%d.%m.%Y")
        H2avg=round(H2prices_filter["H2"].mean(),2)
        H2avg_info=filter_status
        H2max=H2prices_filter["H2"].max()
        H2max_date=H2prices_filter.loc[H2prices_filter["H2"]==H2max,"Data"].iloc[-1].strftime("%d.%m.%Y")
    
        filter_val=[H2min,H2min_date,H2avg,H2avg_info,H2max,H2max_date]

        self.update_widgets(filter_val,H2prices_filter,start_date)
        self.update_plot(H2prices_filter,numticks,rotation)

            
    def update_widgets(self,filter_val,H2prices_filter,start_date):
        self.canvas.itemconfig(self.H2min_Lab,text=filter_val[0])
        self.canvas.itemconfig(self.H2min_date_Lab,text=filter_val[1])

        self.canvas.itemconfig(self.H2avg_Lab,text=filter_val[2])
        self.canvas.itemconfig(self.H2avg_info_Lab,text=filter_val[3])

        self.canvas.itemconfig(self.H2max_Lab,text=filter_val[4])
        self.canvas.itemconfig(self.H2max_date_Lab,text=filter_val[5])

        self.canvas.itemconfig(self.plot_Lab,text=f"od {start_date.strftime('%d.%m.%Y')} do {current_date.strftime('%d.%m.%Y')}")

        
    def update_plot(self,H2prices_filter,numticks,rotation):
        x_arg=H2prices_filter["Data"]
        y_arg=H2prices_filter["H2"]

        self.ax.clear()
        
        self.ax.fill_between(x=x_arg,y2=y_arg,y1=H2prices_filter["H2"].min(),color="#2087d6",alpha=0.15)
        self.ax.plot(x_arg,y_arg,color="#2087d6")
        self.ax.tick_params(color="#403f3f",labelcolor="white",labelsize=10)
        self.ax.tick_params(axis="x",rotation=rotation)
        self.ax.margins(x=0,y=0.01)

        self.ax.xaxis.set_major_locator(ticker.LinearLocator(numticks=numticks))
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%y"))
        self.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))

        plt.grid(color="#403f3f")
        
        self.fig.canvas.draw()

        
    def return_btn(self): #Destroy current window and open parent one
        self.window.destroy()
        self.parent.deiconify()




class Data():
    def __init__(self):
        self.db_table_1="prices"
        self.db_table_2="H2_contract"
        
        self.cols=["Data","ON","Woda","Energia","H2"]
        self.cols_dtypes={"Data":"datetime64[ns]",
                         "ON":"float",
                         "Woda":"float",
                         "Energia":"float",
                         "H2":"float"}


    def read_db(self):
        global conn

        #Check if db exist
        try: #Read db and update it automatically if necessary
            conn=sqlite3.connect("H2price_data.db")
            last_prices_df=pd.read_sql_query(f"SELECT * FROM {self.db_table_1}",conn,dtype=self.cols_dtypes)
            H2contr_df=pd.read_sql_query(f"SELECT * FROM {self.db_table_2}",conn,dtype=self.cols_dtypes)
            prices_df=last_prices_df
            last_date=last_prices_df.iloc[-1,0]           
            if last_date != current_date: #Check daily update status
                prices_df=self.update(last_date,last_prices_df=last_prices_df)
                self.write_db(prices_df)     
        except pd.io.sql.DatabaseError: #Create db
            prices_df=self.update(init_date)
            last_prices_df=prices_df
            H2contr_df=pd.DataFrame(columns=self.cols)
            self.write_db(prices_df,H2contr_df)

        prices_30=self.prices_30(prices_df)

        return last_prices_df, prices_df, prices_30, H2contr_df

        
    def update(self,last_date,last_prices_df=None,water_price=None,energy_price=None):
        if last_prices_df is None: #Init empty df during first run of program
            last_prices_df=pd.DataFrame(columns=self.cols)
        
        if water_price: #Update water price column
            last_prices_df.loc[last_prices_df["Data"]>=last_date,"Woda"]=float(water_price)
            prices_df=last_prices_df
        elif energy_price: #Update energy price column
            last_prices_df.loc[last_prices_df["Data"]>=last_date,"Energia"]=float(energy_price)
            prices_df=last_prices_df
        else:       
            #Update date column
            date_df=pd.DataFrame({"Data":[date for date in pd.date_range(last_date,current_date,inclusive="right")]})

            #Update diesel price column
            diesel_prices=self.get_diesel(last_date)
            diesel_df=date_df.merge(diesel_prices,on="Data",how="outer")
            prices_df=pd.concat([last_prices_df,diesel_df],ignore_index=True)
            
        #Fill NaN values with previous existing price
        prices_df.ffill(inplace=True)
        prices_df.fillna(0,inplace=True)
        
        #Update calculated prices of H2
        #prices_df.loc[prices_df["Data"]>=last_date,"H2"]= ...calculation algorithm - hidden for privacy reasons...

        return prices_df
    

    def prices_30(self,prices_df): #Method that returns H2 prices from last 30 days
        H2_min=prices_df.loc[prices_df["Data"]>=date_30,"H2"].min()
        H2_avg=round(prices_df.loc[prices_df["Data"]>=date_30,"H2"].mean(),2)
        H2_max=prices_df.loc[prices_df["Data"]>=date_30,"H2"].max()

        return H2_min, H2_avg, H2_max


    def write_db(self,prices_df=None,H2contr_df=None):
        if prices_df is not None:
            prices_df.to_sql(self.db_table_1,conn,if_exists="replace",dtype=self.cols_dtypes,index=False)
        if H2contr_df is not None:
            H2contr_df.to_sql(self.db_table_2,conn,if_exists="replace",dtype=self.cols_dtypes,index=False)


    def get_diesel(self,last_date): #Method that webscrap diesel prices
        diesel_prices=pd.read_html('https://spot.lotosspv1.pl/3/type,oil_eurodiesel/hurtowe_ceny_paliw/archiwum_cen_paliw')
        diesel_prices=diesel_prices[0].iloc[:,[0,1]]
        diesel_prices=diesel_prices.rename(columns={"Data zmiany":"Data","Cena":"ON"})
        diesel_prices=diesel_prices.astype({"Data":'datetime64[ns]',"ON":'string'})
        diesel_prices=diesel_prices.loc[diesel_prices["Data"]>last_date]
        diesel_prices["ON"]=diesel_prices["ON"].str.replace(",",".")
        diesel_prices["ON"]=diesel_prices["ON"].str.replace(" ","")
        diesel_prices["ON"]=round(pd.to_numeric(diesel_prices["ON"])/1000,2)

        return diesel_prices

        


if __name__=="__main__":
    data=Data()
    read_data=data.read_db()

    main=Main()
    main.root.mainloop()
