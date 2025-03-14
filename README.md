An app that receives a video as input and returns a chart representing the facial expressions' presence through the video. 
The video is processed by passing certain frames through a persoanlly developed Convolutional Neural Network, trained on a keggle dataset, using keras library in Python. The video and results are then stored in a MongoDB database, being available for accessing later by the user that uploaded the recording. This process is also available for live recordings, the video being analysed in real-time.

Main functionalities:
  - Facial expressions' analysis through a video
  - Keeping a history of each user's analysed videos and their results
  - Downloading frames for which the CNN is very confident to match a facial expression, perfect for using in other clustering tasks involving facial expressions

Technologies used:
  - Python(Streamlit library for frontend, Keras library for training the AI model)
  - FastAPI
  - Docker

A demo of the app is available in " "
The project's structure can be seen in " "
