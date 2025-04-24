import tkinter as tk
from tkinter import ttk
import random


MEM_ROWS     = 10
MEM_COLS     = 20
CACHE_SIZE   = 8
ACCESS_COUNT = 30

class MemorySimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador MP + Cache")

        
        self.mem_values    = [[0]*MEM_COLS for _ in range(MEM_ROWS)]
        self.cache_values  = []
        self.access_list   = []
        self.access_order  = []   

        
        self.mem_cells     = []
        self.cache_cells   = []
        self.lb_access     = None
        self.delay_scale   = None

        
        self.running             = False
        self.current_order_pos   = 0
        self.scan_coords         = []
        self.scan_step_idx       = 0

        self._build_ui()

    def _build_ui(self):
        
        frame_mp = ttk.LabelFrame(self, text="Memória Principal")
        frame_mp.grid(row=0, column=0, padx=5, pady=5)
        for r in range(MEM_ROWS):
            row = []
            for c in range(MEM_COLS):
                lbl = tk.Label(frame_mp, text="000", width=4,
                               relief="ridge", bg="white")
                lbl.grid(row=r, column=c, padx=1, pady=1)
                row.append(lbl)
            self.mem_cells.append(row)

       
        frame_cache = ttk.LabelFrame(self, text="Cache")
        frame_cache.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        for i in range(CACHE_SIZE):
            lbl = tk.Label(frame_cache, text="", width=4,
                           relief="ridge", bg="white")
            lbl.grid(row=0, column=i, padx=1, pady=1)
            self.cache_cells.append(lbl)

        
        frame_list = ttk.LabelFrame(self, text="Lista de Acesso")
        frame_list.grid(row=0, column=1, rowspan=2,
                        padx=5, pady=5, sticky="ns")
        self.lb_access = tk.Listbox(frame_list,
                                    height=20, width=8,
                                    selectmode="extended")
        self.lb_access.pack(padx=5, pady=5)

        
        ctrl = ttk.Frame(self)
        ctrl.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(ctrl, text="Preencher MP",
                   command=self.fill_memory).grid(row=0, column=0, padx=3)
        ttk.Button(ctrl, text="Gerar Lista",
                   command=self.make_access_list).grid(row=0, column=1, padx=3)
        ttk.Button(ctrl, text="Limpar Cache",
                   command=self.clear_cache).grid(row=0, column=2, padx=3)
        ttk.Button(ctrl, text="Iniciar Simulação",
                   command=self.start_simulation).grid(row=0, column=3, padx=3)
        ttk.Button(ctrl, text="Parar",
                   command=self.stop_simulation).grid(row=0, column=4, padx=3)
        ttk.Button(ctrl, text="Limpar Seleção",
                   command=self.clear_selection).grid(row=0, column=5, padx=3)
        self.delay_scale = tk.Scale(ctrl, from_=50, to=1000,
                                    orient="horizontal",
                                    label="Delay (ms)")
        self.delay_scale.set(200)
        self.delay_scale.grid(row=0, column=6, padx=10)

    
    def fill_memory(self):
        for r in range(MEM_ROWS):
            for c in range(MEM_COLS):
                v = random.randint(0, 999)
                self.mem_values[r][c] = v
                self.mem_cells[r][c].config(text=f"{v:03}", bg="white")

    def make_access_list(self):
        self.access_list.clear()
        self.lb_access.delete(0, tk.END)
        for _ in range(ACCESS_COUNT):
            r = random.randrange(MEM_ROWS)
            c = random.randrange(MEM_COLS)
            v = self.mem_values[r][c]
            self.access_list.append(v)
            self.lb_access.insert(tk.END, f"{v:03}")

    def clear_cache(self):
        self.cache_values.clear()
        for lbl in self.cache_cells:
            lbl.config(text="", bg="white")

    
    def start_simulation(self):
        if not self.access_list:
            tk.messagebox.showwarning("Aviso", "Gere a lista de acesso antes.")
            return

        
        sel = list(self.lb_access.curselection())
        if sel:
            self.access_order = sel
        else:
            self.access_order = list(range(len(self.access_list)))

        
        self.lb_access.selection_clear(0, tk.END)
        for row in self.mem_cells:
            for lbl in row:
                lbl.config(bg="white")
        self.clear_cache()

        self.running = True
        self.current_order_pos = 0
        self.after(0, self._process_next_access)

    def stop_simulation(self):
        self.running = False

    def clear_selection(self):
        self.lb_access.selection_clear(0, tk.END)
        for row in self.mem_cells:
            for lbl in row:
                lbl.config(bg="white")
        for lbl in self.cache_cells:
            lbl.config(bg="white")

    def _process_next_access(self):
        if not self.running:
            return
        if self.current_order_pos >= len(self.access_order):
            self.running = False
            return

        idx = self.access_order[self.current_order_pos]
        valor = self.access_list[idx]
        print(f"Processando item {idx}: {valor:03}")

        
        self.scan_step_idx = 0
        self.current_index = idx   
        self.after(0, self._cache_scan_step)

    def _cache_scan_step(self):
        if not self.running:
            return

        
        if 0 < self.scan_step_idx <= CACHE_SIZE:
            self.cache_cells[self.scan_step_idx-1].config(bg="white")

        
        if self.scan_step_idx >= CACHE_SIZE:
            self.scan_coords   = [(r, c) for r in range(MEM_ROWS) for c in range(MEM_COLS)]
            self.scan_step_idx = 0
            self.after(0, self._memory_scan_step)
            return

        
        self.cache_cells[self.scan_step_idx].config(bg="lightblue")
        valor = self.access_list[self.current_index]

        
        if (self.scan_step_idx < len(self.cache_values)
            and self.cache_values[self.scan_step_idx] == valor):
            self.after(self.delay_scale.get(),
                       lambda idx=self.scan_step_idx: self._on_cache_hit(idx))
        else:
            self.scan_step_idx += 1
            self.after(self.delay_scale.get(), self._cache_scan_step)

    def _on_cache_hit(self, cache_idx):
        v = self.access_list[self.current_index]
        
        self.cache_cells[cache_idx].config(bg="lightgreen")
        for r in range(MEM_ROWS):
            for c in range(MEM_COLS):
                if self.mem_values[r][c] == v:
                    self.mem_cells[r][c].config(bg="lightgreen")
                    break
            else:
                continue
            break

        
        self.lb_access.selection_set(self.current_index)

        self.current_order_pos += 1
        self.after(self.delay_scale.get(), self._process_next_access)

    def _memory_scan_step(self):
        if not self.running:
            return

        if self.scan_step_idx > 0:
            pr, pc = self.scan_coords[self.scan_step_idx-1]
            self.mem_cells[pr][pc].config(bg="white")

        if self.scan_step_idx >= len(self.scan_coords):
            return

        r, c = self.scan_coords[self.scan_step_idx]
        self.mem_cells[r][c].config(bg="yellow")
        v = self.access_list[self.current_index]

        if self.mem_values[r][c] == v:
            self.after(self.delay_scale.get(),
                       lambda rr=r, cc=c: self._on_memory_found(rr, cc))
        else:
            self.scan_step_idx += 1
            self.after(self.delay_scale.get(), self._memory_scan_step)

    def _on_memory_found(self, r, c):
        v = self.access_list[self.current_index]
        
        self.mem_cells[r][c].config(bg="white")
        if len(self.cache_values) >= CACHE_SIZE:
            self.cache_values.pop(0)
        self.cache_values.append(v)

        
        for i, lbl in enumerate(self.cache_cells):
            if i < len(self.cache_values):
                val = self.cache_values[i]
                lbl.config(text=f"{val:03}",
                           bg="lightcoral" if i == len(self.cache_values)-1 else "white")
            else:
                lbl.config(text="", bg="white")

        
        self.mem_cells[r][c].config(bg="lightcoral")

        
        self.lb_access.selection_set(self.current_index)

        self.current_order_pos += 1
        self.after(self.delay_scale.get(), self._process_next_access)


if __name__ == "__main__":
    app = MemorySimulator()
    app.lift()
    app.attributes('-topmost', True)
    app.after(0, lambda: app.attributes('-topmost', False))
    app.mainloop()
