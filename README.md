# data-transfer-cloud


This project implements a secure cloud-based file transfer system using the Diffie-Hellman Key Exchange (DHKE) algorithm. It is built with Flask (Python) and deployed on an AWS EC2 instance. The system ensures encrypted communication and file handling through the generation of a shared secret key between parties over an insecure channel, providing confidentiality and integrity in file exchange.

##  About the Project

In an era where digital communication is prevalent, ensuring the confidentiality of data exchanged over networks is crucial. This project addresses this by integrating DHKE to allow secure key generation between users, enabling encrypted file transfers. Registered users can upload text files, generate secure keys, and download encrypted content, ensuring end-to-end security.

The files are processed and stored on the server using unique identifiers, minimizing the chances of file conflicts or unauthorized access. The system is suitable for academic, enterprise, or research-based secure file sharing where confidentiality is a key concern.

## Technologies Used

- **Frontend:** HTML, CSS (via Flask Templates)
- **Backend:** Python with Flask
- **Security:** Diffie-Hellman Key Exchange Algorithm
- **Deployment Platform:** Amazon Web Services (AWS EC2 - Linux instance)

## System Architecture

The project follows a client-server model with secure key exchange and file encryption capabilities:

- Users interact with a simple web interface developed using Flask.
- Upon file upload, the client and server exchange public keys via DHKE.
- A shared secret is computed to encrypt and decrypt file contents.
- Encrypted files are stored securely in unique server-side directories.
- Users can later download the decrypted version using the same shared key.

## Features

- Secure file upload and download with encryption
- Key generation using Diffie-Hellman algorithm
- Cloud-hosted and accessible over the web
- Lightweight and easy-to-use web interface
- User-specific file handling for enhanced security

## Installation and Deployment

### Prerequisites

- Python 3.x
- Flask
- AWS account with an EC2 Linux instance
- Git

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/secure-cloud-transfer-dhke.git
   cd secure-cloud-transfer-dhke
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the Flask server:
   ```bash
   python app.py
   ```

4. Access the app in your browser:
   ```
   http://<EC2-Public-IP>:5000
   ```

## Security

- Public-private key exchange is performed using Diffie-Hellman.
- The shared secret is used to encrypt files using symmetric encryption techniques.
- Files are saved with unique names to avoid conflict or tampering.
- Communication is handled via Flask routes secured within the application logic.
