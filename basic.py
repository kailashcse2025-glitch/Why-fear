

import google.generativeai as genai
from datetime import datetime
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import re 


GEMINI_API_KEY = "AIzaSyABuo0blEzLdPCRsKlxsLa2sMpPgQHFqfQ"
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_forgetfulness_sync(memories, schedule):
    """Performs the synchronous AI call in a separate thread."""
    prompt = f"""
You are an AI specialized in predicting what a person might forget tomorrow.

Here is the user's schedule for tomorrow:
{schedule}

Here are the things they remembered at night:
{memories}

Based on both, give:
1. Things they are most likely to forget (items, tasks, timings, preparation)
2. Missing follow-ups they should not overlook
3. Objects they need to carry
4. Preparations to do early morning
5. One final safety reminder

Keep it short but extremely helpful. Use **bold** text and emojis for a good summary.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"


class SmartNightHelperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        
        self.title("🌙 Smarter Night Memory Helper")
        self.geometry("1000x650")
        
        
        ctk.set_appearance_mode("Dark")  
        ctk.set_default_color_theme("blue") 

        
        self.night_memory = []
        self.tomorrow_schedule = []
        self.forgotten_history = []
        
       
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(7, weight=1)

        ctk.CTkLabel(self.navigation_frame, text="Night Helper", compound="left",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=20, pady=20)

       
        self.home_button = self.create_nav_button("Home", 1, self.home_event)
        self.add_memory_button = self.create_nav_button("Add Memory/Schedule", 2, self.add_memory_event)
        self.view_data_button = self.create_nav_button("View All Data", 3, self.view_data_event)
        self.log_forgot_button = self.create_nav_button("Log Forgotten Incident", 4, self.log_forgot_event)
        self.ai_analysis_button = self.create_nav_button("AI Analysis 🧠", 5, self.ai_analysis_event)
        self.clear_data_button = self.create_nav_button("Clear All Data", 6, self.clear_data_event)
        
        
        ctk.CTkButton(self.navigation_frame, text="Exit", fg_color="red", hover_color="#990000",
                      command=self.destroy).grid(row=8, column=0, padx=20, pady=20, sticky="s")


       
        self.home_frame = HomeScreen(self)
        self.input_frame = InputScreen(self)
        self.view_frame = ViewScreen(self)
        self.forgotten_frame = ForgottenInputScreen(self)
        self.ai_frame = AIAnalysisScreen(self)

        self.frames = {
            "Home": self.home_frame,
            "Input": self.input_frame,
            "View": self.view_frame,
            "Forgotten": self.forgotten_frame,
            "AI": self.ai_frame
        }
        
        
        for name, frame in self.frames.items():
            frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
            
       
        self.select_frame_by_name("Home")

    def create_nav_button(self, text, row, command):
        button = ctk.CTkButton(self.navigation_frame, text=text, 
                               command=command, corner_radius=0, 
                               height=40, border_spacing=10, 
                               fg_color="transparent", 
                               text_color=("gray10", "gray90"), 
                               hover_color=("gray70", "gray30"), anchor="w")
        button.grid(row=row, column=0, sticky="ew")
        return button

    def select_frame_by_name(self, name):
        """Switches the view to the selected frame."""
        for frame_name, button in {
            "Home": self.home_button,
            "Input": self.add_memory_button,
            "View": self.view_data_button,
            "Forgotten": self.log_forgot_button,
            "AI": self.ai_analysis_button
        }.items():
            button.configure(fg_color=("gray75", "gray25") if name == frame_name else "transparent")
            
        frame = self.frames.get(name)
        if hasattr(frame, 'refresh_content'):
            frame.refresh_content()
            
        frame.tkraise()

    
    def home_event(self): self.select_frame_by_name("Home")
    def add_memory_event(self): self.select_frame_by_name("Input")
    def view_data_event(self): self.select_frame_by_name("View")
    def log_forgot_event(self): self.select_frame_by_name("Forgotten")
    def ai_analysis_event(self): self.select_frame_by_name("AI")

  
    def clear_data_event(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear ALL stored data (Memory, Schedule, History)?"):
            self.night_memory.clear()
            self.tomorrow_schedule.clear()
            self.forgotten_history.clear()
            
            
            for frame in self.frames.values():
                if hasattr(frame, 'refresh_content'):
                    frame.refresh_content()
            
            messagebox.showinfo("Success", "All data cleared!")

    def update_data(self, data_type, value):
        """Central method to update the state lists."""
        if data_type == "add_memory":
            self.night_memory.append(value)
            messagebox.showinfo("Success", "Night memory saved!")
        elif data_type == "add_schedule":
            self.tomorrow_schedule.append(value)
            messagebox.showinfo("Success", "Added to schedule!")
            
        
        for frame in self.frames.values():
            if hasattr(frame, 'refresh_content'):
                frame.refresh_content()
        
        self.select_frame_by_name("Home") 




class HomeScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.master = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self, text="Welcome to the Smart Night Helper!", 
                     font=ctk.CTkFont(size=24, weight="bold"), text_color="#FFD700").grid(row=0, column=0, pady=20)
        
        ctk.CTkLabel(self, text="Use the sidebar to manage your memories, schedule, and get AI predictions for forgetfulness.", 
                     font=ctk.CTkFont(size=14)).grid(row=1, column=0, pady=10)
        
        
        self.overview_frame = ctk.CTkFrame(self)
        self.overview_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        self.overview_frame.grid_columnconfigure((0, 1), weight=1)
        
      
        ctk.CTkLabel(self.overview_frame, text="Night Memories (Last 3)", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=10, pady=10)
        self.memory_preview = ctk.CTkLabel(self.overview_frame, text="", justify="left", wraplength=400)
        self.memory_preview.grid(row=1, column=0, padx=10, pady=5, sticky="nsw")
        
        
        ctk.CTkLabel(self.overview_frame, text="Tomorrow's Schedule (Last 3)", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1, padx=10, pady=10)
        self.schedule_preview = ctk.CTkLabel(self.overview_frame, text="", justify="left", wraplength=400)
        self.schedule_preview.grid(row=1, column=1, padx=10, pady=5, sticky="nsw")
        
    def refresh_content(self):
        """Update the quick preview lists."""
        mem_list = self.master.night_memory[-3:]
        sch_list = self.master.tomorrow_schedule[-3:]
        
        mem_text = "\n".join([f"• {m}" for m in mem_list]) if mem_list else "No memories recorded."
        sch_text = "\n".join([f"• {s}" for s in sch_list]) if sch_list else "No schedule recorded."
        
        self.memory_preview.configure(text=mem_text)
        self.schedule_preview.configure(text=sch_text)


class InputScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.master = master
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="Add New Item", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=20)
        
        self.radio_var = tk.StringVar(value="memory")
        
        
        ctk.CTkRadioButton(self, text="Night Memory", variable=self.radio_var, value="memory").grid(row=1, column=0, pady=5)
        ctk.CTkRadioButton(self, text="Tomorrow's Schedule", variable=self.radio_var, value="schedule").grid(row=2, column=0, pady=5)
        
        
        ctk.CTkLabel(self, text="Enter Item/Task:", font=ctk.CTkFont(size=14)).grid(row=3, column=0, pady=(20, 5))
        self.input_entry = ctk.CTkEntry(self, width=400, height=35, font=ctk.CTkFont(size=14))
        self.input_entry.grid(row=4, column=0, pady=10)
        
        ctk.CTkButton(self, text="Save Item", command=self.submit_data, fg_color="green").grid(row=5, column=0, pady=20)

    def refresh_content(self):
        self.input_entry.delete(0, tk.END)
        self.input_entry.focus_set()

    def submit_data(self):
        value = self.input_entry.get().strip()
        data_type = self.radio_var.get()
        
        if not value:
            messagebox.showerror("Error", "Input cannot be empty!")
            return

        target = "add_memory" if data_type == "memory" else "add_schedule"
        self.master.update_data(target, value)
        self.input_entry.delete(0, tk.END)


class ViewScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.master = master
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="Full Data View", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, columnspan=2, pady=20)

      
        mem_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        mem_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        mem_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(mem_frame, text="Night Memories", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=5)
        self.memory_view = scrolledtext.ScrolledText(mem_frame, width=35, height=25, bg="#1a1a1a", fg="#ffffff", wrap=tk.WORD, state=tk.DISABLED)
        self.memory_view.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

     
        sch_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        sch_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        sch_frame.grid_columnconfigure(0, weight=1)
        
        self.tab_view = ctk.CTkTabview(sch_frame)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tab_view.add("Schedule")
        self.tab_view.add("Forgotten History")
        
       
        self.schedule_view = scrolledtext.ScrolledText(self.tab_view.tab("Schedule"), width=35, height=20, bg="#1a1a1a", fg="#ffffff", wrap=tk.WORD, state=tk.DISABLED)
        self.schedule_view.pack(padx=10, pady=10, fill="both", expand=True)

     
        self.history_view = scrolledtext.ScrolledText(self.tab_view.tab("Forgotten History"), width=35, height=20, bg="#1a1a1a", fg="#DDA0DD", wrap=tk.WORD, state=tk.DISABLED)
        self.history_view.pack(padx=10, pady=10, fill="both", expand=True)
        
    def populate_textbox(self, textbox, data_list, is_history=False):
        textbox.configure(state=tk.NORMAL)
        textbox.delete("1.0", tk.END)
        
        if not data_list:
            textbox.insert(tk.END, "No items recorded yet.")
        else:
            if is_history:
                for entry in reversed(data_list):
                    text = f"🗓️ Date: {entry['date']}\n💡 Item: {entry['item']}\n📝 Incident: {entry['description']}\n\n"
                    textbox.insert(tk.END, text)
            else:
                for i, item in enumerate(data_list, 1):
                    textbox.insert(tk.END, f"{i}. {item}\n")
                    
        textbox.configure(state=tk.DISABLED)

    def refresh_content(self):
        """Update all three data views."""
        self.populate_textbox(self.memory_view, self.master.night_memory)
        self.populate_textbox(self.schedule_view, self.master.tomorrow_schedule)
        self.populate_textbox(self.history_view, self.master.forgotten_history, is_history=True)


class ForgottenInputScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.master = master
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="Log Forgotten Incident", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=20)
        
       
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(input_frame, text="1. Forgotten Item (e.g., umbrella, wallet):", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.item_entry = ctk.CTkEntry(input_frame, width=500, height=35, font=ctk.CTkFont(size=14))
        self.item_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(input_frame, text="2. Describe the Incident (What happened and when?):", font=ctk.CTkFont(size=14)).grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")
        self.desc_text = ctk.CTkTextbox(input_frame, width=500, height=150, font=ctk.CTkFont(size=14), wrap="word")
        self.desc_text.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkButton(self, text="Log Incident 📝", command=self.log_incident, fg_color="#FF4500", hover_color="#B23300").grid(row=2, column=0, pady=30)
        
    def refresh_content(self):
        self.item_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.item_entry.focus_set()

    def log_incident(self):
        item = self.item_entry.get().strip()
        desc = self.desc_text.get("1.0", tk.END).strip()
        date = datetime.now().strftime("%d-%m-%Y")

        if not item or not desc:
            messagebox.showerror("Error", "Both item and description are required!")
            return

        self.master.forgotten_history.append({
            "date": date,
            "item": item,
            "description": desc
        })
        messagebox.showinfo("Success", "Forgotten incident saved!")
        self.master.select_frame_by_name("Home")


class AIAnalysisScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.master = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        ctk.CTkLabel(self, text="AI Prediction: What Will I Forget?", font=ctk.CTkFont(size=24, weight="bold"), text_color="#00FFFF").grid(row=0, column=0, pady=20)

      
        self.data_preview = scrolledtext.ScrolledText(self, width=80, height=8, bg="#1a1a1a", fg="#e0e0e0", state=tk.DISABLED, wrap=tk.WORD)
        self.data_preview.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.ask_ai_btn = ctk.CTkButton(self, text="Ask AI for Prediction", command=self.start_ai_analysis, 
                                        fg_color="#8A2BE2", hover_color="#6A5ACD", font=ctk.CTkFont(size=16, weight="bold"))
        self.ask_ai_btn.grid(row=2, column=0, pady=20)
        
        ctk.CTkLabel(self, text="AI Analysis Result:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=3, column=0, pady=(5, 0), sticky="nw", padx=20)
        
      
        self.result_display = scrolledtext.ScrolledText(self, width=80, height=80, bg="#2a140d", fg="#ffffff", state=tk.DISABLED, wrap=tk.WORD)
        self.result_display.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def populate_textbox(self, textbox, text):
        textbox.configure(state=tk.NORMAL)
        textbox.delete("1.0", tk.END)
        textbox.insert(tk.END, text)
        textbox.configure(state=tk.DISABLED)

    def refresh_content(self):
        """Update the data preview box."""
        memory = "\n".join([f"• {m}" for m in self.master.night_memory])
        schedule = "\n".join([f"• {s}" for s in self.master.tomorrow_schedule])
        
        text = f"--- Night Memories ---\n{memory or 'None'}\n\n"
        text += f"--- Tomorrow's Schedule ---\n{schedule or 'None'}"
        
        self.populate_textbox(self.data_preview, text)
        self.populate_textbox(self.result_display, "Press the button above to get a new analysis.")
        
    def start_ai_analysis(self):
        if not self.master.tomorrow_schedule:
            messagebox.showerror("Error", "Add at least one scheduled task before asking for analysis.")
            return

        self.ask_ai_btn.configure(state=tk.DISABLED, text="AI Thinking... ⏳")
        self.populate_textbox(self.result_display, "⏳ AI is analyzing your data... Please wait.")
  
        threading.Thread(target=self.run_analysis_thread, daemon=True).start()

    def run_analysis_thread(self):
        """Thread worker function to run synchronous AI call."""
        joined_memory = ", ".join(self.master.night_memory) if self.master.night_memory else "No night memories"
        joined_schedule = ", ".join(self.master.tomorrow_schedule)
        
        result = analyze_forgetfulness_sync(joined_memory, joined_schedule)
        
        self.master.after(0, self.display_analysis_result, result)

    def display_analysis_result(self, result):
        """Update the result display in the main GUI thread and clean markdown."""
        
    
        cleaned_result = re.sub(r'\*\*', '', result)
        cleaned_result = re.sub(r'\*', '', cleaned_result)
        
        self.ask_ai_btn.configure(state=tk.NORMAL, text="Ask AI for Prediction")
        self.populate_textbox(self.result_display, cleaned_result)



if __name__ == "__main__":
    app = SmartNightHelperApp()
    app.mainloop()
