import random
import sys

import numpy as np
from PIL import Image
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap, QColor, QPen, QFont
from PyQt5.QtWidgets import QApplication, QGraphicsTextItem, QPushButton, QLineEdit
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsEllipseItem, QMainWindow

# Define external data

locationCapital = "Coordinates2.txt"
movingObject1 = "redpin.png"
movingObject2 = "confirm.png"
backgroundObject = "Equirectangular.jpg"


# Process coordinates

def process_coordinates(document):
    """ Save coordinates from textfile to matrix list of strings/floats.

    :param document: document on which the datasetcoor of location and lat long is saved (.txt)
    :return datasetcoor [i][4](matrix list of strings/floats):
    Sets of coordinates and location (country, capital, long, lat)


    This function reads in the document with data.
    It processes the data by removing all unnecessary literals and formats it in a list.
    It then returns the data.
    """

    # open document with coordinates and locations
    with open(document, 'r') as text:
        # save the document to string "coord"
        coord = text.read()

    # creates a list of the string by separating it with newlines
    datasetcoor = coord.split("\n")

    # iterate through list datasetcoor
    for i, listdata in enumerate(datasetcoor):
        # creates a list of 4 elements of each element of "datasetcoor" (result is a matrix)
        datasetcoor[i] = datasetcoor[i].split(",", 3)

        # strip datasetcoor of unnecessary literals
        datasetcoor[i][0] = datasetcoor[i][0].strip('[')
        datasetcoor[i][3] = datasetcoor[i][3].strip(']')

        # make float of string
        datasetcoor[i][2] = float(datasetcoor[i][2])
        datasetcoor[i][3] = float(datasetcoor[i][3])

    return datasetcoor


def adjust_coordinates(tupelmatrix):
    """ Adjust set of coordinates of previous function to coordinates of background PixmapItem

    :param tupelmatrix of type matrix
    :return fit Dataaset Matrix of coordinates and location [country, capital, x, y] [string,string,int,int]

    Matrix[2] = north = y, Matrix[3] = west = x
    tupe
    """

    # Load used background image to determine size of it in pixel
    image1 = Image.open(backgroundObject)
    sizewest, sizenorth = image1.size

    # iterate through list dataset
    for i, listdata in enumerate(tupelmatrix):
        #  Convert long/lat variables into pixel
        # - (minus) tupelmatrix[2] to correct direction from 0 in north and 180 in south of longitude variable
        tupelmatrix[i][2] = int((-tupelmatrix[i][2] + 90) * (sizenorth / 180))
        tupelmatrix[i][3] = int((tupelmatrix[i][3] + 180) * (sizewest / 360))
    return tupelmatrix


def get_scale(image):
    """ Defines an object of type MovingObject(PixmaptItem) and add to canvas


    :param image: (string): name of image of filetype .png or .jpg
    :return object of type PixmapItem, containing image of input

    Defines an object of external class Moving Object in which further properties are defined
    """

    # Load used background image to determine size of it in pixel
    image1 = Image.open(backgroundObject)
    sizewest, sizenorth = image1.size

    # Load used foreground image (needle) to determine size of it in pixel
    image2 = Image.open(image)
    sizewidth, sizeheight = image2.size

    # sizewest/sizewidth / scalefactor = 15
    # Set ratio from backgroundobject to foregroundobject to 20
    scalefactor = sizewest / sizewidth
    scalemove = scalefactor / 4

    return scalemove


lat_long = process_coordinates(locationCapital)
adj_lat_long = adjust_coordinates(lat_long)
scale = get_scale(backgroundObject)


# Elements of interactive window

class MovingObject(QGraphicsPixmapItem):
    """ Set pixmap environment for foreground needle

        ...

        Methods
        -------
        createMovingObject
            Defines an object PixmapItem
        hoverEnterEvent
            Enable hover event and change cursor to hand while hovering over object
        hoverLeaveEvent
            Change back cursor to default
        mousePressEvent
            No event when mouse is pressed
        mouseMoveEvent
            Calculate the position of the mouse after moving
        mouseReleaseEvent
            Print the new mouse position

        Use a class to rewrite mouseevents
        """

    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        self.objectscoorx = int
        self.objectscoory = int

    # Mouse hover event
    def hoverEnterEvent(self, event):
        """ Change mouse to an open hand cursor once touching the object

        :param -
        :return -
        """
        pass

    def hoverLeaveEvent(self, event):
        """ Change back mouse from previous override once leaving the object

        :param -
        :return -
        """
        pass

    # Mouse click event
    def mousePressEvent(self, event):
        """ No event when mouse is pressed

        :param -
        :return -
        """

    def mouseMoveEvent(self, event):
        """ Refresh cursor location to place object of class in new location

        :param -
        :return -
        """
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        orig_position = self.scenePos()

        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        """ Print the new location of the mouse/ object

        :param -
        :return -
        """
        print('MovingObject x {0}, y {1}'.format(self.pos().x(), self.pos().y()))
        self.objectscoorx = self.pos().x()
        self.objectscoory = self.pos().y()


class Point(QGraphicsEllipseItem):
    """ Set an Point to visualize captials on map

            ...

            Methods
            -------
            createEllipse
                Creates an object of type Pixmap with according specifications
            """

    def __init__(self):
        QGraphicsEllipseItem.__init__(self)

        self.coordset = np.zeros(4)

        # Create object of type QGraphicsEllipseItem
        self.ellin = QGraphicsEllipseItem()
        self.ellout1 = QGraphicsEllipseItem()
        self.ellout2 = QGraphicsEllipseItem()

    def create_ellipse(self, citycoordx, citycoordy):
        """ Creates a circle with defined color and coordinates

            :param -
            :return QGraphicsEllipseItem shaped as a circle with set coordinates
            :return QGraphicsEllipseItem shaped as a circle with set coordinates
            :return QGraphicsEllipseItem shaped as a circle with set coordinates

        """

        # Inner circle

        # Set set of coordinates to Ellipse and shape ellipse as a circle
        # coordset[3] resembles latitude and therefore the carthesian x value, coordset[2] longitude = y
        # Recenter ellipse with Coordset - radius/2 origin coordinates at 0,0 of x,y
        self.ellin.setRect(citycoordx - 5, citycoordy - 5, 10, 10)

        # Set the boundary color of the Pen to yellow (sets painter style)
        self.ellin.setPen(QColor("white"))

        # Set the filling color to yellow (sets painter style)
        self.ellin.setBrush(QColor("white"))

        # Outercircle 1

        # Set set of coordinates to Ellipse and shape ellipse as a circle
        # coordset[3] resembles latitude and therefore the carthesian x value, coordset[2] longitude = y
        # Recenter ellipse with Coordset - radius/2 origin coordinates at 0,0 of x,y
        self.ellout1.setRect(citycoordx - 20, citycoordy - 20, 40, 40)

        # Set color and line width of circle
        pen = QPen(Qt.white, 4)
        self.ellout1.setPen(pen)

        # Set the filling color to yellow (sets painter style)
        self.ellout1.setBrush(QColor("transparent"))

        # Outercircle 2

        # Set set of coordinates to Ellipse and shape ellipse as a circle
        # coordset[3] resembles latitude and therefore the carthesian x value, coordset[2] longitude = y
        # Recenter ellipse with Coordset - radius/2 origin coordinates at 0,0 of x,y
        self.ellout2.setRect(citycoordx - 100, citycoordy - 100, 200, 200)

        # Set color and line width of circle
        pen = QPen(Qt.white, 3, Qt.DotLine)
        self.ellout2.setPen(pen)

        # Set the filling color to yellow (sets painter style)
        self.ellout2.setBrush(QColor("transparent"))

        # Return the specified object
        return self.ellin, self.ellout1, self.ellout2


class BackgroundObject(QGraphicsPixmapItem):
    def __init__(self):
        QGraphicsPixmapItem.__init__(self)

        self.orig_cursor_position = QPointF(100, 100)

    # Mouse click event
    def mousePressEvent(self, event):
        """ Write the cursorposition to variable if mouse is pressed

        :param -
        :return -
        """
        self.orig_cursor_position = event.lastScenePos()

        # pass on the event to parent function and therefore defaultfunction
        super(BackgroundObject, self).mousePressEvent(event)


class InteractiveScene(QtWidgets.QGraphicsView):
    """
    Setup a Canvas of GraphicsView, define properties and embeds PixmapItems

    ...

    Methods
    -------
    resizeEvent
        called at window resize event
    textenter
        called at change of text of textbox
    confirm_action
        called when confirm button is pressed
    continue_new_dataset
        called in defined case when button is pressed
    confirm_show_result
        called after second time the confirm button is pressed
    write_result
        called after set of location iterations is done
    timerEvent
        called after each timeoutevent which is set to 1000ms
    wheelEvent
        Defines motion of mousewheel as zoom in and out
    """

    def __init__(self):
        super(InteractiveScene, self).__init__()

        # Create a Canvas for the map
        self.scenemap = QGraphicsScene()
        self.setScene(self.scenemap)

        # Add background map
        self.worldmappix = QPixmap(backgroundObject)
        self.worldmap = BackgroundObject()
        self.worldmap.setPixmap(self.worldmappix)
        self.scenemap.addItem(self.worldmap)

        # Count the times the button is clicked
        self.confirmcounter = 0
        # Number of iterations /2
        self.iterations = 10
        self.numberbuttonclicked = 2 * self.iterations

        # Defines for functions if confirmbutton is pressed
        self.capitalx = int
        self.capitaly = int
        self.playerx = int
        self.playery = int
        self.diffxkm = int
        self.diffykm = int
        self.distsquarekm = int
        self.distkm = int
        self.distkm = int
        self.scalepolkm = 12713.50 / self.scenemap.height()
        self.scaleaquekm = 12756.27 / self.scenemap.width()

        # Defines for end of iterations of location identification
        self.results = np.zeros((self.iterations, 1))
        self.average = int
        self.percent = int

        # Defines for set of coordinates
        self.coords = np.zeros((2, 1))
        # Defines string for infotext
        self.playertext = ""
        # Defines string for name of user
        self.username = ""

        # If false, no zooming took place, therefore a click places the needle
        # If true,zooming took place and needle is only placed at second click, first is for panning
        self.wheeleventbool = False
        # Variable to scale needle according to zoom event
        self.zoomscale = scale

        # 3 Circlesobject to show capital after button is clicked
        self.NewPoint = Point()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerEvent)
        # Set time to locate capital
        self.timetoloc = 31
        # Countervariable for countertimeoutevents
        self.timercount = self.timetoloc

        # Add needle object
        self.needle1pix = QPixmap(movingObject1)
        self.needle1 = MovingObject()
        self.needle1.setPixmap(self.needle1pix)
        # Set needle with an offset of x,y on scene
        self.needle1.setPos(100, 600)
        # Set offset so that needletip is at origion of pixmap at 0 0
        self.needle1.setOffset(2, - self.needle1pix.height())
        self.needle1.setScale(scale)

        # Add button the scene
        self.confirm = QPushButton("Confirm")
        self.confirm.setToolTip('Click to confirm location')
        self.confirm.resize(240, 80)
        self.confirm.move(1775, 930)
        self.confirm.setFont(QFont("Times", 25))
        # setting backgroundcolor
        self.confirm.setStyleSheet("background-color:grey")
        self.confirm.clicked.connect(self.confirm_action)
        self.scenemap.addWidget(self.confirm)

        # Add plain text object to scene for userinstructions
        self.instructtext = QGraphicsTextItem()
        # Scale text
        self.instructtext.setScale(4)
        # set color, last number is alpha value
        self.instructtext.setDefaultTextColor(QColor(255, 255, 255, 255))
        # set the Font
        self.instructtext.setFont(QFont("Times"))
        # Set potion relative to scene
        self.instructtext.setPos(0, 700)
        # Add the item
        self.instructtext.setPlainText("")
        self.scenemap.addItem(self.instructtext)

        # Add plain text object to scene for userinformation
        self.infotext = QGraphicsTextItem()
        # Scale text
        self.infotext.setScale(3)
        # set color, last number is alpha value
        self.infotext.setDefaultTextColor(QColor(255, 255, 255, 255))
        # set the Font
        self.infotext.setFont(QFont("Times"))
        # Set position relative to scene
        self.infotext.setPos(1900, 10)
        # Set text to textfield infotext
        self.infotext.setPlainText("")
        self.scenemap.addItem(self.infotext)

        # Add plain text object to scene for time
        self.timetext = QGraphicsTextItem()
        # Scale text
        self.timetext.setScale(3)
        # set color, last number is alpha value
        self.timetext.setDefaultTextColor(QColor(255, 255, 255, 255))
        # set the Font
        self.timetext.setFont(QFont("Times"))
        # Set position relative to scene
        self.timetext.setPos(1900, 70)
        # Set text to textfield infotext
        self.timetext.setPlainText("")
        self.scenemap.addItem(self.timetext)

        # Add plain text object to scene for userinformation
        self.nametext = QGraphicsTextItem()
        # Scale text
        self.nametext.setScale(4)
        # set color, last number is alpha value
        self.nametext.setDefaultTextColor(QColor(255, 255, 255, 255))
        # set the Font
        self.nametext.setFont(QFont("Times", 14, ))
        # Set position relative to scene
        self.nametext.setPos(10, 400)
        # Set text to textfield infotext
        self.nametext.setPlainText("")
        self.scenemap.addItem(self.nametext)

        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(10,180)
        self.textbox.setFont(QFont("Times", 14))
        self.textbox.setStyleSheet("color:white;  background-color: rgba(0,0,0,100)")
        self.textbox.setText("    enter your name")
        self.textboxvalue = ""
        self.textbox.textChanged.connect(self.textenter)
        self.scenemap.addWidget(self.textbox)

        # Add a point to the scene at location of needle
        self.loc1, self.loc2, self.loc3 = self.NewPoint.create_ellipse(100, 600)

        # Fit Canvas to Background, worldmap out of _createBackground function
        self.fitInView(self.worldmap, QtCore.Qt.KeepAspectRatio)

        # Preset zoom variable to zero for function wheelEvent
        self._zoom = 0
        # Drag view in alternative to scrollbars
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        # Disable Scrollbars for optical reasons
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setStyleSheet("background-color: black")

    def resizeEvent(self, event):
        """ Capture mainwindow resize event and fit pixmap to new size


                    :param -
                    :return -
                    """

        self.fitInView(self.worldmap, QtCore.Qt.KeepAspectRatio)

    def textenter(self):
        """ Is called by an signal of textbox, caused by a textedit

                    :param -
                    :return -
                """
        self.instructtext.setPlainText("Excellent,\n"
                                       "now confirm.")

    def confirm_action(self):
        """ Call functions to show a city to be located and show the location results

            :param -
            :return -
            This function is only executed if the confirmbutton is pressed
            The first time the confirm button is pressed a dataset is generated
            The following button press shows the result of the location of the needle
            This is done by an if not, else statement
        """
        self.confirmcounter += 1

        # Create a new User at beginning
        if self.confirmcounter == 1:
            # Retrieve textbox entry
            self.username = self.textbox.text()

            # textbox is not required any more, but cant be removed, because a proxywidget was used to
            # add it to the scene (scene.addWidget), this is not an optimal solution to simply move it
            # away from the scene
            self.textbox.move(-100, -100)

            self.nametext.setPlainText("")

        # Iterations of localiation of capitals
        if self.confirmcounter <= self.numberbuttonclicked:

            # Do the first time the confirmbutton is clicked (Modulo operator returns rest of division,
            # true for uneven numbers)
            if self.confirmcounter % 2:

                self.continue_new_dataset()
            # Do the second time the confirmbutton is clicked
            else:

                self.confirm_show_result()

        # End of Iterations, show results
        if self.confirmcounter > self.numberbuttonclicked:
            self.write_results()
            self.confirmcounter = 0

    def continue_new_dataset(self):
        """ Generate a new dataset and set according text

                    :param -
                    :return -
                    This function is executed the first time the confirmbutton is pressed


                """
        # Set timer to count down in localisation process
        self.scenemap.addItem(self.needle1)
        # Start timer, every second, a timeout event is created. Handled by timerEvent
        self.timer.start(1000)

        # Remove circles around city from scene
        self.scenemap.removeItem(self.loc1)
        self.scenemap.removeItem(self.loc2)
        self.scenemap.removeItem(self.loc3)

        # Choose random set of capital name and coordinates
        self.coords = random.choice(adj_lat_long)

        # Add Text with captial name to the scene
        self.instructtext.setPlainText(
            "Use the pin needle \nto locate the city " + self.coords[1])

        # Set the number of iterations (confirmcounter) to textfield infotext
        self.infotext.setPlainText(
            str(int((self.confirmcounter + 1) / 2)) + "/" + str(int(self.numberbuttonclicked / 2)))

        # Update text of confirmbutton
        self.confirm.setText("Confirm")

    def confirm_show_result(self):
        """ Show the results of the userlocation

                    :param -
                    :return -
                    This function is executed the second time the confirmbutton is pressed
                    Calculates the distance between random point and userpoint
                    Gives out according text on screen
                """

        # Stop the timer which was started in continue_new_dataset(self)
        self.timer.stop()
        # Reset time variable to initial value
        self.timercount = self.timetoloc
        # Dont show time during result is shown
        self.timetext.setPlainText("")

        # Calculate Distance
        # Swap x and y coordinates ([3]=x, [2]= y) because of longitude and latitude order
        self.capitalx = (self.coords[3])
        self.capitaly = (self.coords[2])

        # Save actual position of needle
        self.playerx = self.needle1.pos().x()
        self.playery = self.needle1.pos().y()

        # Calculate difference of playerneedle to actual citycoordinates in km
        self.diffxkm = abs(self.capitalx - self.playerx) * self.scaleaquekm
        self.diffykm = abs(self.capitaly - self.playery) * self.scalepolkm

        # Calculate distance of playerneedle to actual citycoordinates in km
        self.distsquarekm = pow(self.diffxkm, 2) + pow(self.diffykm, 2)
        self.distkm = int(pow(self.distsquarekm, 1 / 2))

        # Write to result array
        self.results[int(self.confirmcounter / 2) - 1] = self.distkm

        # Add a point to the scene to show the place of the capital
        self.loc1, self.loc2, self.loc3 = self.NewPoint.create_ellipse(self.coords[3], self.coords[2])
        self.scenemap.addItem(self.loc1)
        self.scenemap.addItem(self.loc2)
        self.scenemap.addItem(self.loc3)

        # Update text
        if self.distkm < 50:
            self.playertext = " Congratulations, superb geographical knowledge."
        elif self.distkm < 150:
            self.playertext = " Congratulations, excellent geographical knowledge."
        elif self.distkm < 300:
            self.playertext = " Nicely done, thats very nearby."
        elif self.distkm < 450:
            self.playertext = " Quite good."
        elif self.distkm < 900:
            self.playertext = " Some inaccuracies."
        elif self.distkm < 2000:
            self.playertext = " At least the right direction."
        else:
            self.playertext = "Oh no, better practice some more."

        self.instructtext.setPlainText(self.playertext
                                       + "\n" + self.coords[1] + " is in " + self.coords[
                                           0] + ". Your distance is " + str(self.distkm) + " km")

        # Update text of confirmbutton and set confirmbutton to False
        self.confirm.setText("Continue")

    def write_results(self):
        """ Write the results on average in percent

                    :param -
                    :return -

                """

        # Show no instructions
        self.instructtext.setPlainText("")

        # Calculate average
        self.average = int(self.results.sum()) / self.results.size

        # Set average to percent, 100% is 100 km on average, 0% is below 1500 on average
        # Formula is derived from the two points above (m*x +b)
        self.percent = int((-0.071 * self.average + 107.1))

        # Percent between 0 and 100 percent
        if 0 < self.percent < 100:
            self.instructtext.setPlainText(self.username + " ,\nyou got " + str(self.percent) + " %.")
        # Percentvalue above 100 percent
        elif self.percent > 100:
            # Write 110 percent and username to textfield
            self.instructtext.setPlainText(self.username + " ,\n Astonishing, you got 110 %.")
        # Percentvalue below 0 percent
        else:
            # Write zero percent and username to textfield
            self.instructtext.setPlainText(self.username + " ,\nyou got 0 %.")

    def timerEvent(self):
        """ Captures the timout event of the timerobject


                    :param -
                    :return -
        Each second a timeutevent is captured and a countdown is counted down.
        The current countdown time is printed to the screen
        When countdowntime is down, a functioncall takes place
                    """

        # Subtract one second each time function is called
        self.timercount = self.timercount - 1
        # Write time to screen till button has to be pressed
        self.timetext.setPlainText(str(self.timercount) + " sec")

        # If time runs out simulate confirm button pressed
        if self.timercount == 0:
            self.confirm_action()

    def wheelEvent(self, event):
        """ Indicates that wheelevent took place


        :param -
        :return -
        """
        #
        self.wheeleventbool = True

        if event.angleDelta().y() > 0:
            factor = 1.25

            self._zoom += 1

        else:
            factor = 0.8
            self._zoom -= 1

        if  self._zoom > 0:
            self.scale(factor, factor)
            # Set zoomfactor for needle
            self.zoomscale = self.zoomscale /factor
            # Zoom needle only to scale of 0.05
            if self.zoomscale > 0.05:
                self.needle1.setScale(self.zoomscale)

        elif self._zoom == 0:
            # Scale back the needle to original size
            self.zoomscale = scale
            self.needle1.setScale(scale)
            # Fit in the background according to ratio
            self.fitInView(self.worldmap, QtCore.Qt.KeepAspectRatio)

        else:
            self._zoom = 0

    def mousePressEvent(self, event):
        """ Indicates if mouse press event took place


                :param -
                :return -
                """
        #
        super(InteractiveScene, self).mousePressEvent(event)
        # If true,zooming took place and needle is only placed at second click, first is for panning
        if self.wheeleventbool == False:
            self.needle1.setPos(self.worldmap.orig_cursor_position)


# Main window

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz around the Earth")

        # Create instances of Graphicsviewobjects
        self.interactivewindow = InteractiveScene()
        self.setCentralWidget(self.interactivewindow)


# Show Window on screen
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    view = MainWindow()
    view.show()
    sys.exit(app.exec_())
