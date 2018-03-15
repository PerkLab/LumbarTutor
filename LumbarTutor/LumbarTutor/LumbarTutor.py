import os, sys, glob
from __main__ import vtk, qt, ctk, slicer
from functools import partial

from Guidelet import GuideletLoadable, GuideletLogic, GuideletTest, GuideletWidget
from Guidelet import Guidelet
import PerkTutorCouchDB
import logging
import time



class LumbarTutor(GuideletLoadable):
  """
  Uses GuideletLoadable class, available at:
  This is designed for freehand lumbar puncture. There is also a LumbarTutor for ultrasound-guided lumbar puncture.  
  """

  def __init__(self, parent):
    GuideletLoadable.__init__(self, parent)
    self.parent.title = "Lumbar Tutor"
    self.parent.categories = [ "Training" ]
    self.parent.dependencies = [ "PerkTutorCouchDB" ]
    self.parent.contributors = [ "Matthew S. Holden (Perk Lab; Queen's University)" ]
    self.parent.helpText = """  """
    self.parent.acknowledgementText = """  """


class LumbarTutorWidget(GuideletWidget):
  """Uses GuideletWidget base class, available at:
  """

  def __init__(self, parent = None):
    GuideletWidget.__init__(self, parent)

  def setup(self):
    GuideletWidget.setup(self)

  def addLauncherWidgets(self):
    GuideletWidget.addLauncherWidgets(self)

    # Launcher settings for databases
    self.databaseSettingsGroupBox = ctk.ctkCollapsibleGroupBox()
    self.databaseSettingsGroupBox.setTitle( "Database settings" )
    self.databaseSettingsGroupBox.collapsed = True
    self.databaseSettingsLayout = qt.QFormLayout( self.databaseSettingsGroupBox )
    self.launcherFormLayout.addRow( self.databaseSettingsGroupBox )

    self.databaseFullRemoteAddressLineEdit = qt.QLineEdit()
    self.databaseFullRemoteAddressLineEdit.setEchoMode( qt.QLineEdit.Password )
    self.databaseSettingsLayout.addRow( "Full remote database address", self.databaseFullRemoteAddressLineEdit )

    self.fileServerSessionLineEdit = qt.QLineEdit()
    self.databaseSettingsLayout.addRow( "File server session name", self.fileServerSessionLineEdit )

    self.fileServerClientLineEdit = qt.QLineEdit()
    self.databaseSettingsLayout.addRow( "File server client path", self.fileServerClientLineEdit )

    settings = slicer.app.userSettings()
    self.databaseFullRemoteAddressLineEdit.setText( settings.value( self.moduleName + "/Configurations/" + self.selectedConfigurationName + "/DatabaseFullRemoteAddress" ) )
    self.fileServerSessionLineEdit.setText( settings.value( self.moduleName + "/Configurations/" + self.selectedConfigurationName + "/FileServerSession" ) )
    self.fileServerClientLineEdit.setText( settings.value( self.moduleName + "/Configurations/" + self.selectedConfigurationName + "/FileServerClient" ) )

    self.databaseFullRemoteAddressLineEdit.connect( 'editingFinished()', self.onDatabaseFullRemoteAddressEdited )
    self.fileServerSessionLineEdit.connect( 'editingFinished()', self.onFileServerSessionEdited )
    self.fileServerClientLineEdit.connect( 'editingFinished()', self.onFileServerClientEdited )


  def onConfigurationChanged(self, selectedConfigurationName):
    GuideletWidget.onConfigurationChanged(self, selectedConfigurationName)

    settings = slicer.app.userSettings()
    self.databaseFullRemoteAddressLineEdit.setText( settings.value( self.moduleName + "/Configurations/" + self.selectedConfigurationName + "/DatabaseFullRemoteAddress" ) )
    self.fileServerSessionLineEdit.setText( settings.value( self.moduleName + "/Configurations/" + self.selectedConfigurationName + "/FileServerSession" ) )
    self.fileServerClientLineEdit.setText( settings.value( self.moduleName + "/Configurations/" + self.selectedConfigurationName + "/FileServerClient" ) )


  def onDatabaseFullRemoteAddressEdited( self ):
    self.guideletLogic.updateSettings( { "DatabaseFullRemoteAddress": str( self.databaseFullRemoteAddressLineEdit.text ) }, self.selectedConfigurationName )


  def onFileServerSessionEdited( self ):
    self.guideletLogic.updateSettings( { "FileServerSession": str( self.fileServerSessionLineEdit.text ) }, self.selectedConfigurationName )


  def onFileServerClientEdited( self ):
    self.guideletLogic.updateSettings( { "FileServerClient": str( self.fileServerClientLineEdit.text ) }, self.selectedConfigurationName )


  def createGuideletInstance(self):
    return LumbarTutorGuidelet(None, self.guideletLogic, self.selectedConfigurationName)


  def createGuideletLogic(self):
    return LumbarTutorLogic()


class LumbarTutorLogic(GuideletLogic):
  """Uses GuideletLogic base class, available at:
  """ #TODO add path

  def __init__(self, parent = None):
    GuideletLogic.__init__(self, parent)
    
    self.addValuesToDefaultConfiguration()

    
  def addValuesToDefaultConfiguration( self ):
    GuideletLogic.addValuesToDefaultConfiguration( self )
    moduleDir = os.path.dirname( slicer.modules.lumbartutor.path )

    settingsDict = {}
    settingsDict[ 'StyleSheet' ] = os.path.join( moduleDir, 'Resources', 'StyleSheets', 'LumbarTutorStyle.qss' ) #overwrites the default setting param of base
    settingsDict[ 'RecordingFilenamePrefix' ] = 'LumbarTutorRec-'
    settingsDict[ 'SavedScenesDirectory' ] = os.path.join( moduleDir, 'SavedScenes' ) #overwrites the default setting param of base
    settingsDict[ 'UltrasoundBrightnessControl' ] = '' #overwrites the default setting param of base
    settingsDict[ 'FileServerLocalDirectory' ] = os.path.join( slicer.app.temporaryPath, "LumbarTutor" )
    
    self.updateSettings( settingsDict, 'Default' )



class LumbarTutorTest(GuideletTest):
  """This is the test case for your scripted module.
  """

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    GuideletTest.runTest(self)
    #self.test_LumbarTutor1() #add applet specific tests here


class LumbarTutorGuidelet( Guidelet ):

  def __init__( self, parent, logic, configurationName = 'Default' ):

    Guidelet.__init__( self, parent, logic, configurationName )
    logging.debug( 'LumbarTutorGuidelet.__init__' )
    
    self.moduleDirectory = os.path.dirname( slicer.modules.lumbartutor.path )

    # Set up main frame
    self.sliceletDockWidget.setObjectName( 'LumbarTutorPanel' )
    self.sliceletDockWidget.setWindowTitle( 'Lumbar Tutor' )
    self.mainWindow.setWindowTitle( 'Lumbar Tutor' )
    self.mainWindow.windowIcon = qt.QIcon( os.path.join( self.moduleDirectory, 'Resources', 'Icons', 'LumbarTutor.png' ) )

    self.layoutManager.setLayout( slicer.vtkMRMLLayoutNode.SlicerLayoutNone )

    # Setup user ID
    self.userID = None
    
    self.userLayouts = dict()
    self.userLayouts[ "Guidance" ] = slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalWidescreenView
    self.userLayouts[ "NoGuidance" ] = slicer.vtkMRMLLayoutNode.SlicerLayoutTwoOverTwoView
    
    # Setup logic for database
    self.createCouchDBLogic()
    
    
  def createFeaturePanels( self ):
    # This function sets up the GUI
    featurePanelList = Guidelet.createFeaturePanels( self )
    self.addActionsToUltrasoundPanel()
    
    # Create and add the login panel
    self.loginCollapsibleButton = ctk.ctkCollapsibleButton()
    self.createLoginPanel()
    
    # Modify the panels for the current setup needs
    self.advancedCollapsibleButton.hide()
    self.ultrasoundCollapsibleButton.hide() # for now
    self.ultrasoundCollapsibleButton.setText( "Recording" )
    
    return [ self.loginCollapsibleButton, self.ultrasoundCollapsibleButton ]
    

  def __del__( self ):#common
    self.cleanup()


  # Clean up when guidelet is closed
  def cleanup( self ): #common
    Guidelet.cleanup( self )
    logging.debug( 'cleanup' )


  def setupConnections( self ):
    logging.debug( 'LumbarTutorGuidelet.setupConnections()' )
    Guidelet.setupConnections( self )
    
    self.loginButton.connect( 'clicked()', self.login )
    self.loginExitButton.connect( 'clicked()', self.onExitButtonClicked )
    self.loginReturnButton.connect( 'clicked()', self.onShowFullSlicerInterfaceClicked )
    
    self.viewAlignmentButton.connect( 'clicked()', self.resetAllViews )
    self.ultrasound.startStopRecordingButton.connect( 'clicked(bool)', self.onStartStopRecordingClicked )    
    self.logoutButton.connect( 'clicked()', self.logout )
    
    slicer.mrmlScene.AddObserver( vtk.vtkCommand.ModifiedEvent, self.updateRecordingsTable )
    
    # Keyboard shortcuts
    if ( not hasattr( self, 'startStopShortcutPlus' ) or self.startStopShortcutPlus is None ):
      self.startStopShortcutPlus = qt.QShortcut( qt.QKeySequence( "+" ), self.sliceletDockWidget )
    self.startStopShortcutPlus.connect( 'activated()', self.ultrasound.startStopRecordingButton.click )


  def setupScene( self ): #applet specific
    logging.debug('setupScene')

    # This will automatically create the ReferenceToRas transform
    Guidelet.setupScene( self )
    self.referenceToRas = self.ultrasound.referenceToRas

    # Transforms
    logging.debug( 'Create transforms' )

    # The transforms to be received from PLUS      
    self.needleToReference = slicer.util.getNode( 'NeedleToReference' )
    if not self.needleToReference:
      self.needleToReference = slicer.vtkMRMLLinearTransformNode()
      self.needleToReference.SetName( 'NeedleToReference' )
      slicer.mrmlScene.AddNode( self.needleToReference )

    self.needleTipToNeedle = slicer.util.getNode( 'NeedleTipToNeedle' )
    if not self.needleTipToNeedle:
      self.needleTipToNeedle = slicer.vtkMRMLLinearTransformNode()
      self.needleTipToNeedle.SetName( 'NeedleTipToNeedle' )
      transformMatrix = self.logic.readTransformFromSettings( 'NeedleTipToNeedle', self.configurationName )
      if transformMatrix:
        self.needleTipToNeedle.SetMatrixTransformToParent( transformMatrix )
      slicer.mrmlScene.AddNode( self.needleTipToNeedle )

    # Models
    logging.debug( 'Create models' )

    self.needleModel = slicer.util.getNode( 'NeedleModel' )
    if not self.needleModel:
      self.needleModel = slicer.modules.createmodels.logic().CreateNeedle(80, 1.0, 0, 0)
      self.needleModel.SetName( 'NeedleModel' )
      
    self.spineModel = slicer.util.getNode( 'SpineVisibleModel' )
    if not self.spineModel:
      self.spineModel = slicer.vtkMRMLModelNode()
      self.spineModel.SetName( 'SpineVisibleModel' )
      self.spineModel.SetScene( slicer.mrmlScene )
      slicer.mrmlScene.AddNode( self.spineModel )
      self.spineModel.CreateDefaultDisplayNodes()
      self.spineModel.GetDisplayNode().SetColor( 0.95, 0.85, 0.55 ) #bone
      self.spineModel.SetAndObservePolyData( vtk.vtkPolyData() )
      
    self.tissueModel = slicer.util.getNode( 'TissueModel' )
    if not self.tissueModel:
      self.tissueModel = slicer.vtkMRMLModelNode()
      self.tissueModel.SetName( 'TissueModel' )
      self.tissueModel.SetScene( slicer.mrmlScene )
      slicer.mrmlScene.AddNode( self.tissueModel )
      self.tissueModel.CreateDefaultDisplayNodes()
      self.tissueModel.GetDisplayNode().SetColor( 0.70, 0.50, 0.40 ) #skin
      self.tissueModel.GetDisplayNode().SetOpacity( 0.4 )
      self.tissueModel.SetAndObservePolyData( vtk.vtkPolyData() )
      
    # Images
    logging.debug( 'Create images' )
    
    self.spineCT = slicer.util.getNode( 'SpineCT' )
    if not self.spineCT:
      self.spineCT = slicer.vtkMRMLScalarVolumeNode()
      self.spineCT.SetName( 'SpineCT' )
      slicer.mrmlScene.AddNode( self.spineCT )

    self.displayImageInSliceViewer( self.spineCT.GetID(), "Red" )
    self.displayImageInSliceViewer( self.spineCT.GetID(), "Yellow" )
    self.displayImageInSliceViewer( self.spineCT.GetID(), "Green" )
    self.displayImageSliceIn3D( "Red", True )
    self.displayImageSliceIn3D( "Yellow", True )
    self.displayImageSliceIn3D( "Green", True )
    
    # Load the spine "scenes"
    # Note: There should be only one spine scene
    logging.debug( 'Create spine scenes' )
    
    spineScenes = glob.glob( os.path.join( self.moduleDirectory, 'Resources', 'SpineScenes', "*.mrb" ) )
    for spine in spineScenes:
      slicer.util.loadScene( spine )

    # Build transform tree
    logging.debug('Set up transform tree')

    self.needleToReference.SetAndObserveTransformNodeID( self.referenceToRas.GetID() )  
    self.needleTipToNeedle.SetAndObserveTransformNodeID( self.needleToReference.GetID() )

    self.needleModel.SetAndObserveTransformNodeID( self.needleTipToNeedle.GetID() )
    
    # Somehow compute the appropriate spine model to display and whether or not to show the 3D view
    selectedSpineModel = slicer.mrmlScene.GetFirstNode( "SpineModel", "vtkMRMLModelNode", False, False )
    
    # Setup the views of the scene appropriately
    self.setLayoutForCurrentUser()
    
    # Display the spine model
    selectedTissueModel = None
    selectedReferenceToRas = None
    selectedSpineCT = None
    if ( selectedSpineModel is not None ):
      selectedTissueModel = selectedSpineModel.GetNodeReference( "LumbarTutor.TissueModel" )
      selectedReferenceToRas = selectedSpineModel.GetNodeReference( "LumbarTutor.ReferenceToRAS" )   
      selectedSpineCT = selectedSpineModel.GetNodeReference( "LumbarTutor.SpineCT" )
    if ( selectedSpineModel is None ):
      self.spineModel.SetAndObservePolyData( vtk.vtkPolyData() )
    else:
      self.spineModel.SetAndObservePolyData( selectedSpineModel.GetPolyData() )      
    if ( selectedTissueModel is None ):
      self.tissueModel.SetAndObservePolyData( vtk.vtkPolyData() )
    else:
      self.tissueModel.SetAndObservePolyData( selectedTissueModel.GetPolyData() )      
    if ( selectedReferenceToRas is None ):
      self.referenceToRas.SetMatrixTransformToParent( vtk.vtkMatrix4x4() )
    else:
      self.referenceToRas.SetMatrixTransformToParent( selectedReferenceToRas.GetMatrixTransformToParent() )
    if ( selectedSpineCT is None ):
      self.spineCT.Copy( slicer.vtkMRMLScalarVolumeNode() )
    else:
      self.spineCT.Copy( selectedSpineCT )
    self.resetAllViews()


    # Ensure that the sequence browser toolbar(s) is not made visible
    sequenceBrowserToolBars = slicer.util.mainWindow().findChildren( "qMRMLSequenceBrowserToolBar" )
    for toolBar in sequenceBrowserToolBars:
      toolBar.connect( 'visibilityChanged(bool)', partial( self.setSequenceBrowserToolBarsVisible, False ) )

    # Hide slice view annotations (patient name, scale, color bar, etc.) as they
    # decrease reslicing performance by 20%-100%
    logging.debug( 'Hide slice view annotations' )
    import DataProbe
    dataProbeUtil=DataProbe.DataProbeLib.DataProbeUtil()
    dataProbeParameterNode=dataProbeUtil.getParameterNode()
    dataProbeParameterNode.SetParameter( 'showSliceViewAnnotations', '0' )

    
  def disconnect( self ):#TODO see connect
    logging.debug( 'LumbarTutor.disconnect()' )
    Guidelet.disconnect( self )
    
    self.loginButton.disconnect( 'clicked()', self.login )
    self.loginExitButton.disconnect( 'clicked()', self.onExitButtonClicked )
    self.loginReturnButton.disconnect( 'clicked()', self.onShowFullSlicerInterfaceClicked )

    self.viewAlignmentButton.disconnect( 'clicked(bool)', self.resetAllViews )
    self.ultrasound.startStopRecordingButton.disconnect( 'clicked(bool)', self.onStartStopRecordingClicked )    
    self.logoutButton.disconnect( 'clicked()', self.logout )
    
    slicer.mrmlScene.RemoveObserver( vtk.vtkCommand.ModifiedEvent, self.updateRecordingsTable )
    
    # Keyboard shortcuts
    self.startStopShortcutPlus.disconnect( 'activated()', self.ultrasound.startStopRecordingButton.click )

    
  def setupTopPanel(self):
    pass

    
  def resetAllViews(self):
    # We want a view from the posterior with the superior up and the left left
    # The spine should be centred
    spineCenter_RAS = [ 0, 0, 0 ]
    if ( self.spineModel is not None ):
      comFilter = vtk.vtkCenterOfMass()
      comFilter.SetInputData( self.spineModel.GetPolyData() )
      comFilter.SetUseScalarsAsWeights( False )
      comFilter.Update()
      spineCenter_RAS = comFilter.GetCenter()
      
    # Setup the cameras for the 3D views
    # Implicit assumption that the spine is rotationally aligned with the RAS coordinate frame
    CAMERA_DISTANCE = 600 #mm # Controls the "zoom"
    CAMERA_CLIPPING_RANGE = [ 0.1, 1000 ] # This is the default clipping range. Change it if you change the camera distance.
    cameraNodes = slicer.mrmlScene.GetNodesByClass( "vtkMRMLCameraNode" )
    if ( cameraNodes.GetNumberOfItems() > 0 ):
      camera0 = cameraNodes.GetItemAsObject( 0 )
      camera0.SetFocalPoint( spineCenter_RAS[ 0 ], spineCenter_RAS[ 1 ] - 50, spineCenter_RAS[ 2 ] )
      camera0.SetPosition( spineCenter_RAS[ 0 ] - CAMERA_DISTANCE, spineCenter_RAS[ 1 ] - 50, spineCenter_RAS[ 2 ] )
      camera0.SetViewUp( 0, 0, 1 )
      camera0.GetCamera().SetClippingRange( CAMERA_CLIPPING_RANGE )

    # For the CT images, take the slice at the origin and centre it
    slicer.vtkMRMLSliceNode.JumpAllSlices( slicer.mrmlScene, 0, 0, 0, slicer.vtkMRMLSliceNode.CenteredJumpSlice )


  def addActionsToUltrasoundPanel( self ):
    # View alignment button
    self.viewAlignmentButton = qt.QPushButton( 'Reset Views' )
    self.viewAlignmentButton.setCheckable( False )
  
    # Recordings table
    self.recordingsTable = qt.QTableWidget()
    self.recordingsTable.setRowCount( 0 )
    self.recordingsTable.setColumnCount( 1 )
    self.recordingsTable.horizontalHeader().setResizeMode( 0, qt.QHeaderView.Stretch )
    self.recordingsTable.setHorizontalHeaderLabels( [ "Recording name" ] )
    
    # Logout
    self.logoutButton = qt.QPushButton( 'Save + Logout' )
    self.logoutButton.setCheckable( False )
    
    # Put them on the GUI
    self.ultrasoundLayout.addRow( self.viewAlignmentButton )
    self.ultrasoundLayout.addRow( qt.QLabel() ) # Blank row for spacing between table and buttons.
    self.ultrasoundLayout.addRow( self.recordingsTable )
    self.ultrasoundLayout.addRow( qt.QLabel() ) # Blank row for spacing between table and buttons.
    self.ultrasoundLayout.addRow( self.logoutButton )
    
    
  def createLoginPanel( self ):
    self.loginCollapsibleButton.setProperty( 'collapsedHeight', 20 )
    self.loginCollapsibleButton.text = "Login"
    self.loginCollapsibleButton.collapsed = False
    self.sliceletPanelLayout.addWidget( self.loginCollapsibleButton )
    
    self.loginLayout = qt.QFormLayout()
    self.loginCollapsibleButton.setLayout( self.loginLayout )
    
    # Login user ID text field
    self.userIDLineEdit = qt.QLineEdit( "" )
    
    # Login button
    self.loginButton = qt.QPushButton( 'Login' )
    self.loginButton.setCheckable( False )
    
    # Exit button
    self.loginExitButton = qt.QPushButton( 'Exit' )
    self.loginExitButton.setCheckable( False )

    # Return button
    self.loginReturnButton = qt.QPushButton( 'Return' )
    self.loginReturnButton.setCheckable( False )
    
    # Put them on the GUI
    self.loginLayout.addRow( self.userIDLineEdit )
    self.loginLayout.addRow( self.loginButton )
    self.loginLayout.addRow( qt.QLabel() )
    self.loginLayout.addRow( self.loginExitButton )
    # self.loginLayout.addRow( self.loginReturnButton ) # For debugging purposes


  def updateRecordingsTable(self, observer, eventid):
    numberOfNodes = slicer.mrmlScene.GetNumberOfNodesByClass( "vtkMRMLSequenceBrowserNode" ) 
    self.recordingsTable.setRowCount( numberOfNodes )

    # If a change has been made to the scene with a new sequence browser node,
    # update the table, displaying the name of the node
    for nodeNumber in xrange( numberOfNodes ):
      currSequenceBrowserNode = slicer.mrmlScene.GetNthNodeByClass( nodeNumber, "vtkMRMLSequenceBrowserNode" )
      recordingsTableItem = qt.QTableWidgetItem( currSequenceBrowserNode.GetName() )

      # Add items to the table
      self.recordingsTable.setItem(nodeNumber, 0, recordingsTableItem)
      
      
  def login( self ):
    self.userID = self.userIDLineEdit.text
    self.userIDLineEdit.setText( "" )

    # Adjust the layout
    if ( not self.setLayoutForCurrentUser() ):
      return
    self.loginCollapsibleButton.hide()
    self.ultrasoundCollapsibleButton.show()
    self.ultrasoundCollapsibleButton.collapsed = False

    # Setup the scene and parameters
    self.parameterNode = self.logic.createParameterNode()
    self.setupConnectorNode()
    self.setupScene()
      
      
  def logout( self ):
    # Stop any ongoing recording
    if ( self.ultrasound.startStopRecordingButton.checked ):
      self.ultrasound.startStopRecordingButton.click() # Simulate the user clicking the stop button before logging out
    
    # Clear the scene and user ID
    slicer.mrmlScene.Clear( 0 )
    self.userID = None

    # Adjust the layout
    self.setLayoutForCurrentUser()
    self.ultrasoundCollapsibleButton.hide()
    self.loginCollapsibleButton.show()
    self.loginCollapsibleButton.collapsed = False
    
    
  def saveRecording( self, browserNode ):
    selectedSpineModel = slicer.mrmlScene.GetFirstNode( "SpineModel", "vtkMRMLModelNode", False, False )
    
    # Create the necessary data fields for saving with Perk Tutor CouchDB
    userID = ( "UserID", str( self.userID ) )
    studyID = ( "StudyID", str( "LumbarTutor" ) )
    trialID = ( "TrialID", str( selectedSpineModel.GetName() ) )
    skillLevel = ( "SkillLevel", str( self.layoutManager.layout ) )
    status = ( "Status", str( "Complete" ) )
    date = ( "Date", time.strftime( "%Y/%m/%d-%H:%M:%S" ) )
    metricsComputed = ( "MetricsComputed", False )
    dataFields = dict( [ userID, studyID, trialID, skillLevel, status, date, metricsComputed ] ) #creates dict from list of tuples, format for saving

    localDirectory = self.parameterNode.GetParameter( "FileServerLocalDirectory" )
    serverSessionName = self.parameterNode.GetParameter( "FileServerSession" )
    serverFtpClient = self.parameterNode.GetParameter( "FileServerClient" )
    self.ptcLogic.uploadSession( dataFields, browserNode, localDirectory, serverSessionName, serverFtpClient )
    
    
  def createCouchDBLogic( self ):
    self.ptcLogic = PerkTutorCouchDB.PerkTutorCouchDBLogic()

    # Attempt to initialize the database if not already initialized
    fullRemoteAddress = self.parameterNode.GetParameter( "DatabaseFullRemoteAddress" )
    try:
      self.ptcLogic.updateDatabase( PerkTutorCouchDB.PERK_TUTOR_DATABASE_NAME, fullRemoteAddress )
    except Exception as e:
      logging.warning( e )
    
    
  def setLayoutForCurrentUser( self ):
    if ( self.userID is None ):
      self.layoutManager.setLayout( slicer.vtkMRMLLayoutNode.SlicerLayoutNone )
      return False
      
    for currUserGroupName in self.userLayouts:
      currUserGroupFile = open( os.path.join( self.moduleDirectory, 'Resources', 'UserGroups', currUserGroupName + ".txt" ) )
      currUserGroupIDs = currUserGroupFile.readlines()
      if ( self.userID in currUserGroupIDs ):
        self.layoutManager.setLayout( self.userLayouts[ currUserGroupName ] )
        return True
        
    logging.info( "LumbarTutorGuidelet::setLayoutForCurrentUser: Could not find user with ID: " + self.userID + "." )
    self.layoutManager.setLayout( slicer.vtkMRMLLayoutNode.SlicerLayoutNone )
    return False
    


  def getCamera( self, viewName ):
    """
    Get camera for the selected 3D view
    """
    camerasLogic = slicer.modules.cameras.logic()
    camera = camerasLogic.GetViewActiveCameraNode( slicer.util.getNode( viewName ) )
    return camera

    
  def displayImageInSliceViewer( self, imageNodeID, sliceName ):
    sliceWidget = slicer.app.layoutManager().sliceWidget( sliceName )
    if ( sliceWidget is None ):
      return
    sliceLogic = sliceWidget.sliceLogic()
    if ( sliceLogic is None ):
      return
    sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID( imageNodeID )    


  def displayImageSliceIn3D( self, sliceName, visible ):
    sliceWidget = slicer.app.layoutManager().sliceWidget( sliceName )
    if ( sliceWidget is None ):
      return
    sliceNode = sliceWidget.sliceView().mrmlSliceNode()
    if ( sliceNode is None ):
      return
    sliceNode.SetSliceVisible( visible )


  def setSequenceBrowserToolBarsVisible( self, visible, wasVisible = False ):
    sequenceBrowserToolBars = slicer.util.mainWindow().findChildren( "qMRMLSequenceBrowserToolBar" )
    for toolBar in sequenceBrowserToolBars:
      toolBar.setVisible( visible )

      
  def startSequenceBrowserRecording( self, browserNode ):
    if ( browserNode is None ):
      return
  
    browserNode.SetName( slicer.mrmlScene.GetUniqueNameByString( self.userID + "-Recording" ) )
    # Create and populate a sequence browser node if the recording started
    browserNode.SetScene( slicer.mrmlScene )
    slicer.mrmlScene.AddNode( browserNode )
    sequenceBrowserLogic = slicer.modules.sequencebrowser.logic()
    
    modifiedFlag = browserNode.StartModify()
    sequenceBrowserLogic.AddSynchronizedNode( None, self.needleToReference, browserNode )
    
    # Stop overwriting and saving changes to all nodes
    browserNode.SetRecording( None, True )
    browserNode.SetOverwriteProxyName( None, False )
    browserNode.SetSaveChanges( None, False )
    browserNode.EndModify( modifiedFlag )

    browserNode.SetRecordMasterOnly( True )
    browserNode.SetRecordingActive( True )
    
    # Hide the slices from 3D
    self.displayImageSliceIn3D( 'Red', False )
    self.displayImageSliceIn3D( 'Yellow', False )
    self.displayImageSliceIn3D( 'Green', False )

    
  def stopSequenceBrowserRecording( self, browserNode ):
    if ( browserNode is None ):
      return
    
    browserNode.SetRecordingActive( False )
    browserNode.SetRecording( None, False )
    
    self.saveRecording( browserNode )
    
    # Show the slices from 3D
    self.displayImageSliceIn3D( 'Red', True )
    self.displayImageSliceIn3D( 'Yellow', True )
    self.displayImageSliceIn3D( 'Green', True )

    
  def onStartStopRecordingClicked(self):    
    if self.ultrasound.startStopRecordingButton.isChecked():
      self.lumbarTutorSequenceBrowserNode = slicer.vtkMRMLSequenceBrowserNode()
      self.startSequenceBrowserRecording( self.lumbarTutorSequenceBrowserNode )
    else:
      self.stopSequenceBrowserRecording( self.lumbarTutorSequenceBrowserNode )
