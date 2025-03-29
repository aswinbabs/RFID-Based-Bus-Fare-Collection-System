# Bus Fare Collection System

This project is an RFID-based bus fare collection system implemented on a Raspberry Pi with GPS tracking and Firebase integration. The system calculates fares based on the distance traveled and updates the user's balance accordingly.

## Features

- **RFID Authentication:** Reads card IDs and retrieves user data from Firebase.
- **GPS-Based Fare Calculation:** Determines the travel distance using the Haversine formula.
- **Dynamic Fare Deduction:** Deducts the appropriate fare based on a distance-based pricing model.
- **Firebase Integration:** Stores user data, travel logs, and updates balances.
- **Admin Travel Logs:** Logs journey details accessible only to admins.
- **Recharge System:** Allows balance top-up via a separate program.

## Hardware Requirements

- Raspberry Pi 
- MFRC522 RFID Module
- RFID Cards
- GPS Module (compatible with Raspberry Pi)
- Internet Connection (for Firebase updates)

## Distance-Based Fare Chart

| Distance (km) | Fare (₹) |
|--------------|----------|
| 0 - 5        | 20       |
| 6 - 10       | 30       |
| 11 - 15      | 40       |
| 16 - 20      | 50       |

## Future Enhancements

- **Payment Gateway Integration** for online balance recharges.
- **Mobile App Support** for real-time balance checks.
- **Improved Security Features** such as encryption for data transmission.

## License

This project is licensed under the MIT License. Feel free to modify and enhance it!

## Contact

For any questions or contributions, reach out via:
 
- **LinkedIn:** [Aswin Babu K](https://www.linkedin.com/in/aswin-babu-k/)
