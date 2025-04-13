# 🚦 Fuzzy Traffic Control System

This project is a simulation of an intelligent traffic control system using **Fuzzy Logic**. Built with Python and Pygame, it visualizes how traffic signals dynamically adjust green light durations based on real-time vehicle behavior.

## 📌 Features

- Real-time vehicle movement simulation
- Dynamic traffic light control using fuzzy logic
- Adjustable vehicle spawn rates (Slow, Medium, Fast)
- Fuzzy rule-based green light extension
- Graphical interface using Pygame

## 🧠 Fuzzy Logic Rules (Sample)

- If **few** vehicles are arriving → **zero** extension.
- If **many** are arriving and **few** behind red → **long** extension.
- If **medium** arriving and **many** behind red → **short** extension.
- Subsequent extensions are limited to avoid unfair delays.

## 📁 Project Structure

```
FUZZY_TRAFFIC_CONTROL/
├── main.py
├── requirements.txt
├── README.md
├── images/
├── src/
│   ├── Simulator.py
│   ├── Config.py
│   ├── Fuzzy.py
│   ├── Common.py
│   ├── Controller/
│   │   ├── TrafficController.py
│   │   ├── VehicleController.py
│   │   └── BackgroundController.py
│   └── Entity/
│       ├── Vehicle.py
│       └── TrafficLight.py
```

## 🚀 How to Run the Project

### 1. Clone or Download

```bash
git clone https://github.com/yourusername/fuzzy-traffic-control.git
cd fuzzy-traffic-control
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Simulator

```bash
python main.py
```

## 🖥️ Controls

| Action | Description |
|--------|-------------|
| Click "Slow/Medium/Fast" | Change spawn rate per direction |
| Auto Fuzzy Logic | Automatically triggered when green time is about to expire |
| Close Window | Quits the simulation |

## 📚 Dependencies

- [Pygame](https://www.pygame.org/)
- [NumPy](https://numpy.org/)
- [scikit-fuzzy](https://pythonhosted.org/scikit-fuzzy/)

## 💡 Future Enhancements

- Add emergency vehicle prioritization
- Export real-time data to logs or CSV
- Integrate with real-world traffic datasets
- Deploy to Raspberry Pi with sensors

## 🧑‍💻 Author

Developed by **Vaishnavi Polampalli**

## 📝 License

This project is licensed under the MIT License.
