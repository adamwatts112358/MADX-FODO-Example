import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patches as mpatches

def write_FODO(filename):
    with open(filename,'w') as f:
        f.write('''
qk1 := 0.250076;
ld = 1.0;
lq = 1.0;
ldipole = 3.0;

D:  DRIFT,      L=0.5*ld;                 
QF: QUADRUPOLE, L=0.5*lq,   K1:=qk1;
QD: QUADRUPOLE, L=0.5*lq,   K1:=-qk1;
B:  RBEND,      L=ldipole,  ANGLE=0.001;

! Markers for PTC observation points
! PTC automatically observers at start and end of the beamline
Obs1: MARKER;
Obs2: MARKER;
Obs3: MARKER;
Obs4: MARKER;
Obs5: MARKER;

FODO: LINE=(QF,D,Obs1,D,B,D,Obs2,D,QD,Obs3,QD,D,Obs4,D,B,D,Obs5,D,QF);

beam,particle=proton,energy=120.0; 
use,period=FODO;

! Run TWISS module in "ring" mode, i.e. find matched solution for initial CS params
twiss, save, file="twiss.out";
''')

def write_FODO_PTC(x, px, y, py, dpp, filename):
    filename = 'FODO_PTC.madx'
    with open(filename,'w') as f:
        f.write('''
qk1 := 0.250076;
ld = 1.0;
lq = 1.0;
ldipole = 3.0;

D:  DRIFT,      L=0.5*ld;                 
QF: QUADRUPOLE, L=0.5*lq,   K1:=qk1;
QD: QUADRUPOLE, L=0.5*lq,   K1:=-qk1;
B:  RBEND,      L=ldipole,  ANGLE=0.001;

! Markers for PTC observation points
! PTC automatically observers at start and end of the beamline
Obs1: MARKER;
Obs2: MARKER;
Obs3: MARKER;
Obs4: MARKER;
Obs5: MARKER;

FODO: LINE=(QF,D,Obs1,D,B,D,Obs2,D,QD,Obs3,QD,D,Obs4,D,B,D,Obs5,D,QF);

beam,particle=proton,energy=120.0;

!=== Begin Particle Tracking Section ===
use,period=FODO;
ptc_create_universe;
ptc_create_layout,time=false;
''')
        for i in range(0,len(x),1):        
                f.write('ptc_start, x= %f, px=%f, y= %f, py=%f, t=0.0, pt=%f;\n'%(x[i],px[i],y[i],py[i],dpp[i]))
        f.write('''
ptc_observe,place=Obs1;
ptc_observe,place=Obs2;
ptc_observe,place=Obs3;
ptc_observe,place=Obs4;
ptc_observe,place=Obs5;

ptc_track,ICASE=5,element_by_element=FALSE,dump,onetable;
ptc_track_end;
ptc_end;
!=== End Particle Tracking Section ===

stop;
''')

def run_MAD(filename):
    os.system(r'madx < {} > out.txt'.format(filename))

def parsetwiss(filename):
    names = []
    keywords = []
    s = []
    betx = []
    bety = []
    alfx = []
    alfy = []
    mux = []
    muy = []
    dx = []
    dy = []
    L = []

    with open(filename,'r') as f:
        lines = f.readlines()
        headers = lines[45].split()
        del headers[0]
        for line in lines[47:]:
            names.append(line.split()[headers.index('NAME')].strip('\"'))
            keywords.append(line.split()[headers.index('KEYWORD')].strip('\"'))
            s.append(float(line.split()[headers.index('S')]))
            betx.append(float(line.split()[headers.index('BETX')]))
            alfx.append(float(line.split()[headers.index('ALFX')]))
            bety.append(float(line.split()[headers.index('BETY')]))
            alfy.append(float(line.split()[headers.index('ALFY')]))
            mux.append(float(line.split()[headers.index('MUX')]))
            muy.append(float(line.split()[headers.index('MUY')]))
            dx.append(float(line.split()[headers.index('DX')]))
            dy.append(float(line.split()[headers.index('DY')]))
            L.append(float(line.split()[headers.index('L')]))
    return names,keywords,s,betx,bety,alfx,alfy,mux,muy,dx,dy,L
    
def plot_twiss(names,keywords,s,betx,bety,dx,dy):   

    box_height = 0.25
    def draw_quad(s_start,length,name,color):
        plt.gca().add_patch(mpatches.Rectangle((s_start, -0.5*box_height), length, box_height, facecolor=color,zorder=10))
        plt.text(s_start+length/2,-1.5*box_height,name,horizontalalignment='center',fontsize=12,rotation='horizontal',color=color)
    def draw_dipole(s_start,length,name,color):
        plt.gca().add_patch(mpatches.Rectangle((s_start, -0.5*box_height), length, box_height, facecolor=color,zorder=10))
        plt.text(s_start+length/2,-1.5*box_height,name,horizontalalignment='center',fontsize=12,rotation='horizontal',color=color)
    def plotMarker(name,height):
        s_val=s[names.index(name)]
        plt.axvline(x=s_val,color='red',linestyle='--')
        plt.text(s_val+0.1,height,name,color='red',rotation=90)

    plt.figure(figsize=(16,8))
    plt.suptitle('FODO example',fontsize=22)

    plt.subplot(311)
    plt.plot(s,[0]*len(s),'k-')
    plt.xlim(0,s[-1])
    plt.ylim(-1,1)
    plt.gca().set_xlim(left=0)
    plt.gca().get_xaxis().set_ticks([])
    plt.gca().get_yaxis().set_ticks([])
    plt.gca().set_facecolor('#f1f1f1')
    # Plot quads and dipoles
    for i in range(len(keywords)):
        if 'QUADRUPOLE' in keywords[i]:
            draw_quad(s[i]-L[i],L[i], names[i], '#CB6015')
        elif 'RBEND' in keywords[i]:
            draw_dipole(s[i]-L[i],L[i], names[i], '#004C97')
        elif 'OBS' in names[i]:
            plotMarker(names[i], 0.6)

    plt.subplot(312)
    plt.plot(s,betx,label=r'$\beta_x$')
    plt.plot(s,bety,label=r'$\beta_y$')
    plt.xlabel('s [m]')
    plt.xlim(0,s[-1])
    plt.ylabel(r'$\beta$ [m]',fontsize=14)
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
    #      ncol=3, fancybox=True, shadow=True)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.gca().set_facecolor("#F8F8F8")
    plt.grid()
    
    plt.subplot(313)
    plt.plot(s,dx,'b',label=r'$D_x [m]$')
    plt.plot(s,dy,'g',label=r'$D_y [m]$')
    plt.xlabel('s [m]')
    plt.xlim(0,s[-1])
    plt.ylabel(r'$D [m]$',fontsize=14)
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
    #      ncol=3, fancybox=True, shadow=True)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.gca().set_facecolor("#F8F8F8")
    plt.grid()
    
    #plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.savefig('plot_twiss.png')    
    
def makeParticles(alpha,beta,e,nparticles):
    gamma = (1+alpha**2)/beta
    sigmax = (e*beta)**0.5
    sigmaxp = (e*gamma)**0.5
    m = 0.5*np.arctan((2*alpha)/(gamma - beta))
    x = np.random.normal(0,sigmax,nparticles)
    xp = m*x + np.random.normal(0,sigmaxp,nparticles)
    
    return x,xp
    
def parse_tracking_output(filename,nparticles):
    # Don't forget to pass number of obs points
    x_new = [[] for i in range(10)]
    y_new = [[] for i in range(10)]
    px_new = [[] for i in range(10)]
    py_new = [[] for i in range(10)]
    
    with open(filename,'r') as f:
        lines = f.readlines()

    n = 0
    for i in range(0,len(lines[8:]),1):
        if '#segment' in lines[i]:
            for j in range(i+1,i+nparticles+1,1):
                try:
                    x_new[n].append(float(lines[j].split()[2]))
                    px_new[n].append(float(lines[j].split()[3]))
                    y_new[n].append(float(lines[j].split()[4]))
                    py_new[n].append(float(lines[j].split()[5]))
                except:
                    pass
            n=n+1
    return x_new, px_new, y_new, py_new

def get_CS_params(x,xp):
    x = np.asarray(x)
    xp = np.asarray(xp)
    
    s11 = np.mean(x**2)
    s12 = np.mean(x*xp)
    s22 = np.mean(xp**2)
    
    epsilon = (s11*s22 - s12**2)**0.5
    beta = s11/epsilon
    alpha = -s12/epsilon
    gamma = (1+alpha**2)/beta
    
    return alpha, beta, gamma, epsilon
    
def draw_ellipse(alpha,beta,gamma,epsilon):
    # Plots the RMS (one-sigma) ellipse
    x_ellipse = np.linspace(-(epsilon*beta)**0.5,(epsilon*beta)**0.5,100)
    xp_pos = (1/beta)*(-alpha*x_ellipse + (alpha**2*x_ellipse**2+beta*epsilon-beta*gamma*x_ellipse**2)**0.5)
    xp_neg = (1/beta)*(-alpha*x_ellipse - (alpha**2*x_ellipse**2+beta*epsilon-beta*gamma*x_ellipse**2)**0.5)
    plt.plot(x_ellipse,xp_pos,'r',linewidth=2)
    plt.plot(x_ellipse,xp_neg,'r',linewidth=2)

def PSplot(x,xp,y,yp,title):
    # Ensure numpy arrays
    x = np.asarray(x)
    xp = np.asarray(xp)
    y = np.asarray(y)
    yp = np.asarray(yp)
    
    plt.figure(figsize=(12,6))
    markersize=0.75
    
    plt.suptitle(title)

    alphax, betax, gammax, epsilonx = get_CS_params(x,xp)
    xtextstr = r'$\beta_x = %.2f m$'%(betax)+'\n'+r'$\alpha_x = %.2f$'%(alphax)+'\n'+r'$\epsilon_x (RMS) = %.2f$'%(epsilonx*1E6)+r' $\pi*mm*mr$'
    plt.subplot(121)
    plt.title('Horizontal')
    plt.plot(x,xp,'o',markersize=markersize)
    plt.xlabel('x [m]')
    plt.ylabel('x\' [r]')
    plt.xlim(-3.0*(epsilonx*betax)**0.5, 3.0*(epsilonx*betax)**0.5)
    plt.ylim(-3.0*(epsilonx*betax)**0.5, 3.0*(epsilonx*betax)**0.5)
    plt.ylim()
    plt.gca().set_facecolor('#f1f1f1')
    plt.text(0.04, 0.80, xtextstr, transform=plt.gca().transAxes, fontsize=12, color='red', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    plt.grid()
    draw_ellipse(alphax,betax,gammax,epsilonx)

    alphay, betay, gammay, epsilony = get_CS_params(y,yp)
    ytextstr = r'$\beta_y = %.2f m$'%(betay)+'\n'+r'$\alpha_y = %.2f$'%(alphay)+'\n'+r'$\epsilon_y (RMS) = %.2f$'%(epsilony*1E6)+r' $\pi*mm*mr$'
    plt.subplot(122)
    plt.title('Vertical')
    plt.plot(y,yp,'o',markersize=markersize)
    plt.xlabel('y [m]')
    plt.ylabel('y\' [r]')
    plt.xlim(-3.0*(epsilony*betay)**0.5, 3.0*(epsilony*betay)**0.5)
    plt.ylim(-3.0*(epsilony*betay)**0.5, 3.0*(epsilony*betay)**0.5)
    plt.gca().set_facecolor('#f1f1f1')
    plt.text(0.50, 0.80, ytextstr, transform=plt.gca().transAxes, fontsize=12, color='red', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    plt.grid()
    draw_ellipse(alphay,betay,gammay,epsilony)

    plt.tight_layout()
    
    plt.savefig(title+'.png')
    

# Write the MADX input deck for the FODO lattice to get the matched CS params
write_FODO('FODO.madx')
run_MAD('FODO.madx')

# Read TWISS output and plot the results
names,keywords,s,betx,bety,alfx,alfy,mux,muy,dx,dy,L = parsetwiss('twiss.out')
plot_twiss(names,keywords,s,betx,bety,dx,dy)

# Write a new FODO_PTC deck with vectors from the matched CS params from above
nparticles = 1000
ex = 10.0E-6 # Physical (geometric, non-normalized emittance), units of [pi*m*r]
ey = 10.0E-6 # Physical (geometric, non-normalized emittance), units of [pi*m*r]
x, px = makeParticles(alfx[0],betx[0],ex,nparticles)
y, py = makeParticles(alfy[0],bety[0],ey,nparticles) # note, don't forget conversion between px and yp
dpp = [1.0E-4]*nparticles
write_FODO_PTC(x, px, y, py, dpp, 'FODO_PTC.madx')
run_MAD('FODO_PTC.madx')

# Parse the PTC output
x_PTC, px_PTC, y_PTC, py_PTC = parse_tracking_output('trackone',nparticles)

# Plot phase space for each observation point
n_obs_points = 7 # remember, MADX adds 2
for i in range(n_obs_points):
    PSplot(x_PTC[i],px_PTC[i],y_PTC[i],py_PTC[i], 'Obs{}'.format(i))