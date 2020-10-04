from summarize import *
import threading

text = ['']
filtered_text = filter_text(text)

chunks = list(get_chunks(filtered_text, 16))
final_text = list()
threads = list()

for chunk in chunks:
    t = threading.Thread(target=spell_checker, args=(chunk,final_text))
    threads.append(t)
    t.start()
    
_ = [t.join() for t in threads]

summarizer = Summarizer(final_text)
summary = summarizer.get_summary()