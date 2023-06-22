import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button

# Set up the figure and axis
fig, ax = plt.subplots()

# Set the limits of the plot
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)

# Create a quiver plot for the magnetic field
X, Y = np.meshgrid(np.arange(-10, 10, 1), np.arange(-10, 10, 1))
U = -Y / (X**2 + Y**2)
V = X / (X**2 + Y**2)
q = ax.quiver(X, Y, U, V)

# Create a scatter plot for the two particles
scat = ax.scatter([5, -5], [0, 0], c=['r', 'b'])

# Define the update function for the animation
def update(i):
    # Rotate the position of the particles
    x = 5 * np.cos(np.radians(i))
    y = 5 * np.sin(np.radians(i))
    scat.set_offsets([[x, y], [-x, -y]])

    # Update the magnetic field
    U = -(Y - y) / ((X - x)**2 + (Y - y)**2) + (Y + y) / ((X + x)**2 + (Y + y)**2)
    V = (X - x) / ((X - x)**2 + (Y - y)**2) - (X + x) / ((X + x)**2 + (Y + y)**2)
    q.set_UVC(U, V)

# Create the animation
ani = FuncAnimation(fig, update, frames=np.arange(0, 360), interval=50)

# Add a button to pause and resume the animation
paused = False
def on_click(event):
    global paused
    if paused:
        ani.event_source.start()
        paused = False
    else:
        ani.event_source.stop()
        paused = True

pause_ax = plt.axes([0.7, 0.025, 0.1, 0.04])
pause_button = Button(pause_ax, 'Pause')
pause_button.on_clicked(on_click)

# Show the plot
plt.show()
