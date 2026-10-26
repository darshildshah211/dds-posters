import sys, wave, numpy as np, soundfile as sf
def load_music(p):
    with wave.open(p) as w: return np.frombuffer(w.readframes(w.getnframes()),"<i2").astype(np.float32)/32767, w.getframerate()
def mix(music_wav, voice_items, out, dur, SR=44100):
    m,sr=load_music(music_wav); n=int(dur*SR); m=np.pad(m,(0,max(0,n-len(m))))[:n]
    v=np.zeros(n,np.float32); env=np.zeros(n,np.float32)
    for path,t0 in voice_items:
        x,r=sf.read(path); x=x.astype(np.float32)
        x=np.interp(np.linspace(0,len(x)-1,int(len(x)*SR/r)),np.arange(len(x)),x)
        i0=int(t0*SR); i1=min(n,i0+len(x)); v[i0:i1]+=x[:i1-i0]; env[i0:i1]=1
    k=int(0.25*SR); env=np.convolve(env,np.ones(k)/k,mode="same")
    mus=m*(1-0.6*env)
    v=v/ max(1e-6,np.abs(v).max())*0.9
    o=mus*0.9+v; o/=max(1,np.abs(o).max()/0.95)
    with wave.open(out,"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((o*32767).astype("<i2").tobytes())
