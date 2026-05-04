// Get Led A, B, C, D road
int AR = 3;
int AG = 4;

int BR = 5;
int BG = 6;

int CR = 7;
int CG = 8;

int DR = 9;
int DG = 10;

String command = "";
bool isAuto = true;

bool isDouble = false;
int old_rPin = 0;
int old_gPin = 0;


void setup() {
  // Initialize Serial incomming command
  Serial.begin(9600);
  
  int pins[] = {AR, AG, BR, BG, CR, CG, DR, DG};
  for ( int i = 0; i < 8; i++) {
    pinMode(pins[i], OUTPUT);
  }

  Serial.println("Smart Traffic Light System is On");
}

void allRed() {
  int reds[] = {AR, BR, CR, DR};
  int greens[] = {AG, BG, CG, DG};

  for ( int i = 0; i < 4; i++) {
    analogWrite(reds[i], 255);
    analogWrite(greens[i], 0);
  }
}

void autoTraffic() {
  old_rPin = 0;
  old_gPin = 0;
  
  // Road A
  allRed();

  analogWrite(AR, 0);
  analogWrite(AG, 255);  
  delay(5000);
  
  analogWrite(AR, 255);
  analogWrite(AG, 255);
  delay(1000);

  // Road B
  allRed();
  
  analogWrite(BR, 0);
  analogWrite(BG, 255);  
  delay(5000);
  
  analogWrite(BR, 255);
  analogWrite(BG, 255);
  delay(1000);
  
  // Road C
  allRed();
  
  analogWrite(CR, 0);
  analogWrite(CG, 255);  
  delay(5000);
  
  analogWrite(CR, 255);
  analogWrite(CG, 255);
  delay(1000);

  // Road D
  allRed();

  analogWrite(DR, 0);
  analogWrite(DG, 255);  
  delay(5000);
  
  analogWrite(DR, 255);
  analogWrite(DG, 255);
  delay(1000);
}

void handleDoubleRoad() {
      // Road AC
      allRed();

      analogWrite(AR, 0);
      analogWrite(AG, 255);

      analogWrite(CR, 0);
      analogWrite(CG, 255);
      delay(5000);
      
      analogWrite(AR, 255);
      analogWrite(AG, 255);
      
      analogWrite(CR, 255);
      analogWrite(CG, 255);
      delay(1000);

      // Road BD
      allRed();
      
      analogWrite(BR, 0);
      analogWrite(BG, 255);
      
      analogWrite(DR, 0);
      analogWrite(DG, 255);  
      delay(5000);
      
      analogWrite(BR, 255);
      analogWrite(BG, 255);

      analogWrite(DR, 255);
      analogWrite(DG, 255);  
      delay(1000);
      
}

// for yellow light time to work

void OpenRoad(int rPin, int gPin) {
  analogWrite(old_rPin, 255);
  analogWrite(old_gPin, 255);
  delay(1000);
  
  old_rPin = rPin;
  old_gPin = gPin;

  allRed();
  analogWrite(rPin, 0);
  analogWrite(gPin, 255);
}

void OpenRoadWithTimer(int rPin, int gPin, int time) {
  allRed();
  analogWrite(rPin, 0);
  analogWrite(gPin, 255);
  delay(time);

  analogWrite(rPin, 255);
  analogWrite(gPin, 255);
  delay(1000);
  
  isAuto = true;
}

void handleSerial() {
  
  if (Serial.available() > 0) {
    isAuto = false;
    String command = Serial.readStringUntil('\n');

    command.trim();

    if(command.startsWith("OPEN:")) {
      isDouble = false;
      
      char road = command.charAt(5);

      if (road == 'A') OpenRoad(AR, AG);
      if (road == 'B') OpenRoad(BR, BG);
      if (road == 'C') OpenRoad(CR, CG);
      if (road == 'D') OpenRoad(DR, DG);
      
      Serial.print("Open road : ");
      Serial.print(command);

    } 
    
    else if (command.startsWith("DOUBLE")) {
      isDouble = true;
    }

    else if (command.startsWith("TIME:")) {
      char road = command.charAt(5);
      String timeStr = command.substring(6);
      int newTime = timeStr.toInt();

      if ( road == 'A' ) {
        OpenRoadWithTimer(AR, AG, newTime);
      }
      
      if ( road == 'B' ) {
        OpenRoadWithTimer(BR, BG, newTime);
      }

      if ( road == 'C' ) {
        OpenRoadWithTimer(CR, CG, newTime);
      }

      if ( road == 'D' ) {
        OpenRoadWithTimer(DR, DG, newTime);
      }      
    }
    else if (command == "SET_AUTO") {
      isAuto = true;
      isDouble = false;
    }
  }
}


void loop() {

  handleSerial();

  if(isDouble) {
    handleDoubleRoad();
  }

  if(isAuto) {
    analogWrite(old_rPin, 255);
    analogWrite(old_gPin, 255);
    delay(1000);

    autoTraffic();
  }
}