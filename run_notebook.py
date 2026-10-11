"""Execute the primary notebook from a clean local kernel; contains no experiment logic."""
import os
import subprocess
import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient

root=Path(__file__).resolve().parent
os.chdir(root)
prefix=root/'.cache/jupyter'
os.environ['IPYTHONDIR']=str(root/'.cache/ipython')
subprocess.run([sys.executable,'-m','ipykernel','install','--prefix',str(prefix),'--name','rag-assignment','--display-name','RAG Assignment'],check=True)
os.environ['JUPYTER_PATH']=str(prefix/'share/jupyter')
os.environ['IPYTHONDIR']=str(root/'.cache/ipython')
os.environ['JUPYTER_RUNTIME_DIR']=str(root/'.cache/jupyter-runtime')
path=root/'RAG_Baseline_vs_Reranking.ipynb'
notebook=nbformat.read(path,as_version=4)
# Clear outputs so stale observations cannot survive an execution failure.
for cell in notebook.cells:
    if cell.cell_type=='code': cell.outputs=[];cell.execution_count=None
client=NotebookClient(notebook,timeout=1800,kernel_name='rag-assignment',resources={'metadata':{'path':str(root)}})
try:
    client.execute()
finally:
    nbformat.write(notebook,path)
print('Clean-kernel execution succeeded:',path.name)
