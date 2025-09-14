-- Creating Tables And Defining Schema


CREATE TABLE Providers (
    Provider_ID INT NOT NULL,
    Name VARCHAR(255),
    Type VARCHAR(100),
    Address VARCHAR(500),
    City VARCHAR(100),
    Contact VARCHAR(100)
    --CONSTRAINT PK_Providers PRIMARY KEY NONCLUSTERED (Provider_ID) NOT ENFORCED
);


CREATE TABLE Receivers (
    Receiver_ID INT NOT NULL,
    Name VARCHAR(255),
    Type VARCHAR(100),
    City VARCHAR(100),
    Contact VARCHAR(100)
    --CONSTRAINT PK_Receivers PRIMARY KEY NONCLUSTERED (Receiver_ID) NOT ENFORCED
);


CREATE TABLE Food_Listings (
    Food_ID INT NOT NULL,
    Food_Name VARCHAR(255),
    Quantity INT,
    Expiry_Date DATE,
    Provider_ID INT,
    Provider_Type VARCHAR(100),
    Location VARCHAR(255),
    Food_Type VARCHAR(100),
    Meal_Type VARCHAR(100)
    --CONSTRAINT PK_Food_Listings PRIMARY KEY NONCLUSTERED (Food_ID) NOT ENFORCED,
    --CONSTRAINT FK_Food_Provider FOREIGN KEY (Provider_ID) REFERENCES Providers(Provider_ID) NOT ENFORCED
);

CREATE TABLE Claims (
    Claim_ID INT NOT NULL,
    Food_ID INT,
    Receiver_ID INT,
    Status VARCHAR(50),
    [Timestamp] DATETIME2(3)
    --CONSTRAINT PK_Claims PRIMARY KEY NONCLUSTERED (Claim_ID) NOT ENFORCED,
    --CONSTRAINT FK_Claims_Food FOREIGN KEY (Food_ID) REFERENCES Food_Listings(Food_ID) NOT ENFORCED,
    --CONSTRAINT FK_Claims_Receiver FOREIGN KEY (Receiver_ID) REFERENCES Receivers(Receiver_ID) NOT ENFORCED
);


-- Adding Constraints

ALTER TABLE Providers
ADD CONSTRAINT PK_Providers PRIMARY KEY NONCLUSTERED (Provider_ID) NOT ENFORCED

ALTER TABLE Receivers
ADD CONSTRAINT PK_Receivers PRIMARY KEY NONCLUSTERED (Receiver_ID) NOT ENFORCED

ALTER TABLE Food_Listings
ADD CONSTRAINT PK_Food_Listings PRIMARY KEY NONCLUSTERED (Food_ID) NOT ENFORCED

ALTER TABLE Food_Listings
ADD CONSTRAINT FK_Food_Provider FOREIGN KEY (Provider_ID) REFERENCES Providers(Provider_ID) NOT ENFORCED

ALTER TABLE Claims
ADD CONSTRAINT PK_Claims PRIMARY KEY NONCLUSTERED (Claim_ID) NOT ENFORCED

ALTER TABLE Claims
ADD CONSTRAINT FK_Claims_Food FOREIGN KEY (Food_ID) REFERENCES Food_Listings(Food_ID) NOT ENFORCED

ALTER TABLE Claims
ADD CONSTRAINT FK_Claims_Receiver FOREIGN KEY (Receiver_ID) REFERENCES Receivers(Receiver_ID) NOT ENFORCED

-- Populating Values From Data Source


INSERT INTO Providers (Name, Type, Address, City, Contact, Provider_ID) SELECT Name, Type, Address, City, Contact, Provider_ID FROM providers_data;

INSERT INTO Receivers (Name, Type, City, Contact, Receiver_ID) SELECT Name, Type, City, Contact, Receiver_ID FROM receivers_data

INSERT INTO Food_Listings (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type) SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type FROM food_listings_data

INSERT INTO Claims (Status, Timestamp, Claim_ID, Food_ID, Receiver_ID) SELECT Status, Timestamp, Claim_ID, Food_ID, Receiver_ID FROM claims_data












