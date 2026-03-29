SmartCashier Web Application

LIVE DEMO
https://smartcashier-crud-2.onrender.com/

Project Overview

SmartCashier is a web-based cashier system designed to simulate real-world retail operations. It evolved from a CLI-based application into a fully functional web platform using Flask. The system focuses on data integrity, validation, and business logic implementation, making it suitable as both an academic project and portfolio showcase.

Core Features
Authentication System
- User registration with validation rules
- Secure login & session management
- Duplicate user prevention
Product Management (CRUD)
- Add, update, delete products
- Input validation (code, name, price, stock)
- Duplicate product prevention
Transaction Engine
- Multi-item cart system
- Real-time stock validation
- Automatic calculations:
- Subtotal
- Discount (quantity & price based)
- Tax (PPN 11%)
- Grand total
Transaction History
- Track all transactions per user
- Persistent database storage

Business Logic Highlights
This project implements real-world cashier logic:
Stock validation before checkout
- Dual discount system:
  - Quantity-based discount
  - Price-based discount
- Best discount selection (maximum applied)
- Automatic stock update after transaction
- Persistent transaction records

  
