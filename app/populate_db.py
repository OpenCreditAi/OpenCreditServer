from app import db
from app.models import Organization, Loan, User, Offer
from datetime import datetime

# Sample Organization Data with Manual IDs
organizations_data = [
    {"id": 11, "name": "בנק לאומי"},
    {"id": 12, "name": "נדלן"},
    {"id": 13, "name": "בנק הפועלים"},
    {"id": 14, "name": "השקאות"},
]

# Sample User Data
users_data = [
    {
        "id": 11,
        "email": "financier@gmail.com",
        "password": "Aa123456",
        "role": "financier",
        "full_name": "financier",
        "phone_number": "555-123-4567",
        "organization_id": 11,
    },
    {
        "id": 12,
        "email": "borrower1@gmail.com",
        "password": "Aa123456",
        "role": "borrower",
        "full_name": "borrower1",
        "phone_number": "987-654-3210",
        "organization_id": 12,
    },
    {
        "id": 13,
        "email": "financier2@gmail.com",
        "password": "Aa123456",
        "role": "financier",
        "full_name": "financier2",
        "phone_number": "555-123-4567",
        "organization_id": 13,
    },
    {
        "id": 14,
        "email": "borrower2@gmail.com",
        "password": "Aa123456",
        "role": "borrower",
        "full_name": "borrower2",
        "phone_number": "987-654-3210",
        "organization_id": 14,
    },
    {
        "id": 15,
        "email": "financier3@gmail.com",
        "password": "Aa123456",
        "role": "financier",
        "full_name": "financier3",
        "phone_number": "555-123-4567",
        "organization_id": 13,
    },
]

# Sample Loan Data
loans_data = [
    {
        "id": 11,
        "user_id": 12,
        "organization_id": 12,
        "project_type": "מגורים",
        "project_name": "בניין דירות יוקרה בתל אביב",
        "address": "רחוב ארלוזורוב 12, תל אביב",
        "amount": 2500000,  # 2.5 million NIS
    },
    {
        "id": 12,
        "user_id": 12,
        "organization_id": 12,
        "project_type": "מסחר",
        "project_name": "מרכז קניות חדש בנתניה",
        "address": "המרץ 23, נתניה",
        "amount": 5000000,  # 5 million NIS
    },
    {
        "id": 13,
        "user_id": 14,
        "organization_id": 14,
        "project_type": "בנייה עצמית",
        "project_name": "בית פרטי בכפר סבא",
        "address": "רחוב החקלאים 4, כפר סבא",
        "amount": 7500000,  # 7.5 million NIS
    },
    {
        "id": 14,
        "user_id": 12,
        "organization_id": 12,
        "project_type": "מגורים",
        "project_name": "הקמת בניין דירות בחיפה",
        "address": "דרך יפו 100, חיפה",
        "amount": 10000000,  # 10 million NIS
    },
    {
        "id": 15,
        "user_id": 14,
        "organization_id": 14,
        "project_type": "מסחר",
        "project_name": "הקמת סופרמרקט בתל אביב",
        "address": "הדרך 22, תל אביב",
        "amount": 15000000,  # 15 million NIS
    },
    {
        "id": 16,
        "user_id": 12,
        "organization_id": 12,
        "project_type": "בנייה עצמית",
        "project_name": "בית יוקרה ברמת גן",
        "address": "רחוב השושנים 3, רמת גן",
        "amount": 20000000,  # 20 million NIS
    },
    {
        "id": 17,
        "user_id": 14,
        "organization_id": 14,
        "project_type": "מגורים",
        "project_name": "בניין דירות בקיסריה",
        "address": "דרך הים 5, קיסריה",
        "amount": 25000000,  # 25 million NIS
    },
    {
        "id": 18,
        "user_id": 12,
        "organization_id": 12,
        "project_type": "מסחר",
        "project_name": "מרכז מסחרי בהרצליה",
        "address": "הדרך 15, הרצליה",
        "amount": 30000000,  # 30 million NIS
    },
    {
        "id": 19,
        "user_id": 14,
        "organization_id": 14,
        "project_type": "בנייה עצמית",
        "project_name": "הקמת בית פרטי בירושלים",
        "address": "רחוב האורנים 8, ירושלים",
        "amount": 40000000,  # 40 million NIS
    },
    {
        "id": 20,
        "user_id": 12,
        "organization_id": 12,
        "project_type": "מגורים",
        "project_name": "הקמת פרויקט מגורים באשדוד",
        "address": "רחוב החורש 14, אשדוד",
        "amount": 50000000,  # 50 million NIS
    },
]

offers_data = [
    # Loan 11 (בניין דירות יוקרה בתל אביב)
    {
        "id": 1,
        "loan_id": 11,
        "user_id": 12,
        "organization_id": 11,
        "offer_amount": 2500000,
        "interest_rate": 5,
        "offer_terms": "7 years, monthly payments",
        "status": "Accepted",
        "repayment_period": 84,
    },
    {
        "id": 2,
        "loan_id": 11,
        "user_id": 14,
        "organization_id": 13,
        "offer_amount": 1750000,
        "interest_rate": 5.5,
        "offer_terms": "6 years, quarterly payments",
        "status": "Pending",
        "repayment_period": 72,
    },
    
    # Loan 12 (מרכז קניות חדש בנתניה)
    {
        "id": 3,
        "loan_id": 12,
        "user_id": 12,
        "organization_id": 11,
        "offer_amount": 5000000,
        "interest_rate": 6,
        "offer_terms": "5 years, monthly payments",
        "status": "Denied",
        "repayment_period": 60,
    },
    {
        "id": 4,
        "loan_id": 12,
        "user_id": 14,
        "organization_id": 13,
        "offer_amount": 4500000,
        "interest_rate": 5.5,
        "offer_terms": "7 years, quarterly payments",
        "status": "Accepted",
        "repayment_period": 84,
    },
    
    # Loan 13 (בית פרטי בכפר סבא)
    {
        "id": 5,
        "loan_id": 13,
        "user_id": 12,
        "organization_id": 11,
        "offer_amount": 5000000,
        "interest_rate": 4.5,
        "offer_terms": "10 years, annual payments",
        "status": "Pending",
        "repayment_period": 120,
    },
    {
        "id": 6,
        "loan_id": 13,
        "user_id": 14,
        "organization_id": 13,
        "offer_amount": 6000000,
        "interest_rate": 5,
        "offer_terms": "6 years, monthly payments",
        "status": "Denied",
        "repayment_period": 72,
    },    
    # Loan 16 (בית יוקרה ברמת גן)
    {
        "id": 9,
        "loan_id": 16,
        "user_id": 12,
        "organization_id": 11,
        "offer_amount": 10000000,
        "interest_rate": 5,
        "offer_terms": "6 years, monthly payments",
        "status": "Accepted",
        "repayment_period": 72,
    },
    
    # Loan 17 (בניין דירות בקיסריה)
    {
        "id": 11,
        "loan_id": 17,
        "user_id": 14,
        "organization_id": 13,
        "offer_amount": 25000000,
        "interest_rate": 6,
        "offer_terms": "7 years, monthly payments",
        "status": "Pending",
        "repayment_period": 84,
    },
    
    # Loan 18 (מרכז מסחרי בהרצליה)
    {
        "id": 12,
        "loan_id": 18,
        "user_id": 12,
        "organization_id": 11,
        "offer_amount": 30000000,
        "interest_rate": 6.5,
        "offer_terms": "6 years, quarterly payments",
        "status": "Denied",
        "repayment_period": 72,
    },
    
    # Loan 19 (הקמת בית פרטי בירושלים)
    {
        "id": 13,
        "loan_id": 19,
        "user_id": 12,
        "organization_id": 13,
        "offer_amount": 40000000,
        "interest_rate": 5.25,
        "offer_terms": "8 years, monthly payments",
        "status": "Accepted",
        "repayment_period": 96,
    },
    
    # Loan 20 (הקמת פרויקט מגורים באשדוד)
    {
        "id": 14,
        "loan_id": 20,
        "user_id": 12,
        "organization_id": 11,
        "offer_amount": 50000000,
        "interest_rate": 5.25,
        "offer_terms": "10 years, monthly payments",
        "status": "Accepted",
        "repayment_period": 120,
    },
    {
        "id": 15,
        "loan_id": 20,
        "user_id": 14,
        "organization_id": 13,
        "offer_amount": 48000000,
        "interest_rate": 5.75,
        "offer_terms": "9 years, quarterly payments",
        "status": "Pending",
        "repayment_period": 108,
    },
    {
        "id": 19,
        "loan_id": 14,
        "user_id": 12,
        "organization_id": 11,
        "offer_amount": 10000000,
        "interest_rate": 5.2,
        "offer_terms": "6 years, monthly payments",
        "status": "Accepted",
        "repayment_period": 72,
    },
    {
        "id": 21,
        "loan_id": 16,
        "user_id": 14,
        "organization_id": 13,
        "offer_amount": 7500000,
        "interest_rate": 5.9,
        "offer_terms": "10 years, monthly payments",
        "status": "Accepted",
        "repayment_period": 120,
    },
    {
        "id": 22,
        "loan_id": 17,
        "user_id": 14,
        "organization_id": 11,
        "offer_amount": 5000000,
        "interest_rate": 5.2,
        "offer_terms": "6 years, monthly payments",
        "status": "Pending",
        "repayment_period": 72,
    },
    {
        "id": 24,
        "loan_id": 19,
        "user_id": 14,
        "organization_id": 11,
        "offer_amount": 40000000,
        "interest_rate": 6.3,
        "offer_terms": "10 years, annual payments",
        "status": "Pending",
        "repayment_period": 120,
    }
]

# Function to populate the Organization table
def populate_organizations():
    # Create organization records with manual IDs
    organizations = []
    for org_data in organizations_data:
        org = Organization(id=org_data["id"], name=org_data["name"])  # Manually set the ID
        organizations.append(org)

    # Add all organization instances to the session
    db.session.add_all(organizations)

    # Commit the session to save data to the database
    db.session.commit()
    print("Organizations populated successfully with manually set IDs.")
    
    
    

# Function to populate the User table
def populate_users():
    users = []
    for user_data in users_data:
        user = User(
            id=user_data["id"],
            email=user_data["email"],
            role=user_data["role"],
            full_name=user_data["full_name"],
            phone_number=user_data["phone_number"],
            organization_id=user_data["organization_id"],
        )
        user.set_password(user_data["password"])  # Hash the password
        users.append(user)

    # Add all user instances to the session
    db.session.add_all(users)

    # Commit the session to save data to the database
    db.session.commit()
    print("Users populated successfully.")
    

# Function to populate the Loan table
def populate_loans():
    loans = []
    for loan_data in loans_data:
        loan = Loan(
            id=loan_data["id"],
            user_id=loan_data["user_id"],
            organization_id=loan_data["organization_id"],
            project_type=loan_data["project_type"],
            project_name=loan_data["project_name"],
            address=loan_data["address"],
            amount=loan_data["amount"],
        )
        loans.append(loan)

    # Add all loan instances to the session
    db.session.add_all(loans)

    # Commit the session to save data to the database
    db.session.commit()
    print("Loans populated successfully.")
    
    
def populate_offers():
    offers = []
    for offer_data in offers_data:
        offer_s = Offer(
            id=offer_data["id"],
            loan_id=offer_data["loan_id"],
            user_id=offer_data["user_id"],
            organization_id=offer_data["organization_id"],
            offer_amount=offer_data["offer_amount"],
            interest_rate=offer_data["interest_rate"],
            offer_terms=offer_data["offer_terms"],
            status=offer_data["status"],
            repayment_period=offer_data["repayment_period"],
        )
        offers.append(offer_s)

    # Add all offer instances to the session
    db.session.add_all(offers)

    # Commit the session to save data to the database
    db.session.commit()
    print("Offers populated successfully.")
    
def populate():
    populate_organizations()
    populate_users()
    populate_loans()
    populate_offers()