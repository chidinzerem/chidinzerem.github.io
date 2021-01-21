-- MSBX 5405
-- Final Select Statements
use ridex;

-- STORED PROCEDURE

# create procedure driverStats
delimiter //
create procedure driverStats (in driverid int, out totaldriverrevenue decimal(10,2), out totalmiles int, out totalrides int)
begin
	select sum(ride_amt)
	into totaldriverrevenue
	from ride_fact
	where driverid = driver_id;
	
    select sum(miles) 
    into totalmiles
	from ride_fact
	where driverid = driver_id;
    
	select count(driver_id)
    into totalrides
	from ride_fact
	where driverid = driver_id;
    
end//
delimiter ; 

# test procedure

call driverstats(202, @totaldriverrevenue, @totalmiles, @totalrides);
select @totaldriverrevenue, @totalmiles, @totalrides;

call driverstats(207, @totaldriverrevenue, @totalmiles, @totalrides);
select @totaldriverrevenue, @totalmiles, @totalrides;

-- STORED FUNCTION #1

# Create Function RevPerMil
DROP FUNCTION IF EXISTS revPerMile;

DELIMITER //

CREATE FUNCTION revPerMile (id_parm int) RETURNS int
DETERMINISTIC
BEGIN
	DECLARE mile int;
    DECLARE rev int;
    DECLARE revMile int;
    
    SET mile = (SELECT miles
				FROM ride_fact
                WHERE id = id_parm
				);
	
    SET rev = (SELECT SUM(ride_amt)
			   FROM ride_fact
               WHERE id = id_parm
			  );
	
    SET revMile = rev/mile;
    
    RETURN (revMile);
    
END//

DELIMITER ;


-- STORED FUNCTION #2

-- change delimiter
delimiter //
-- create function
create function triplen (trip_id int) returns int
deterministic
begin
declare length int;
select sum(miles)
into length
from ride_fact
where id = trip_id;
return(length);
end//
-- change delimiter
delimiter ;


-- TRIGGER

# create audit table to track former customers
create table cust_audit
(rider_id int, first_name varchar(25), last_name varchar(25),
	joined_date date, cancelled_date date, gender varchar(1), country varchar(45), phone_no varchar(12), dob date); 

# create audit trigger before delete on customer
-- change delimiter
delimiter //
create trigger customer_audit_onDelete
before delete on dim_cust
for each row
begin
	-- insert old value
    insert into cust_audit (rider_id, first_name, last_name, joined_date, cancelled_date, gender, country, phone_no, dob)
    values (old.id, old.first_name, old.last_name, old.joined_date, current_date(), old.gender, old.country, old.phone_no, old.dob);
end //
-- change delimiter 
delimiter ;

# test customer_audit_onDelete trigger
# insert a row of data into dim_cust then delete it and see if the audit table populates with said row of data! 

insert into dim_cust (id, first_name, last_name, joined_date, gender, country, phone_no, dob)
values (127, 'testfirst', 'testlast', '2018-01-01', 'M', 'United States', '917-252-3551', '1998-01-01');

delete from dim_cust
where id = 127;



# Show the customer with the most ‘revenue’ (i.e., ‘revenue’ = sum(Ride_amt).  SUBQUERY

select concat(Dim_Cust.First_Name , ' ' , Dim_Cust.Last_Name) as 'Customer_Name', 
	sum( Ride_Fact.Ride_amt) as 'Revenue'
from Ride_Fact
inner join Dim_Cust
on Ride_Fact.Rider_ID = Dim_Cust.ID
Group by Ride_Fact.Rider_ID
order by Revenue;

# Show the top three customers based on ‘revenue’. Rider_ID, customerName( Concat(First_name, ‘ ‘ , Last_name), 
# and ‘revenue’ columns. Make sure that if two or more customers have the same ‘revenue’, both/all ties are listed.

select RF.Rider_ID, concat(DC.First_Name, ' ' , DC.Last_Name) as 'Cust_Name',
	sum(RF.Ride_amt) as 'Revenue'
from Ride_Fact as RF
inner join Dim_Cust as DC
on DC.ID = RF.Rider_ID
group by RF.Rider_ID 
order by Revenue desc
limit 3;


# Find the top three highest 'valued-orders' for each month (i.e., MONTH(Ride_start_time)) 
# based on revenue (i.e., ‘revenue’ = Count(Rider_ID) * Ride_amt).

with cte
as (select
row_number() over(
partition by month(Ride_Fact.Ride_start_time)
order by sum(Ride_Fact.Ride_amt)desc) Row_Num,
month(Ride_Fact.Ride_start_time) MonthDate, sum(Ride_Fact.Ride_amt) Revenue
from Ride_Fact
group by Ride_Fact.Ride_start_time)

select MonthDate, Revenue, Row_num
from cte
where row_num <= 3
having revenue > 0;



# Show the ‘total revenue’ by Driver_ID . Show only Drivers with more than 3 Rides 
#	in ‘Count(driver_ID).’ Order by highest to lowest revenue. 

select RF.Driver_ID, count(RF.Ride_start_time) as 'Rides'
from Ride_Fact as RF
group by RF.Driver_ID
having count(RF.Ride_start_time) > 3
;

# How many orders were less than 10$?
select RF.Ride_amt, RF.Rider_id
from Ride_Fact RF
where RF.Ride_amt < 10
;


# Ranked drivers by revenue
select
concat(first_name,' ',last_name) as driver
,sum(ride_amt) as revenue
,rank() over(order by sum(ride_amt) desc) as driver_rank
from dim_driver as d
join ride_fact as r
on d.id = r.driver_id
group by 1;

# Ranked customers by revenue

select
concat(first_name,' ',last_name) as rider
,sum(ride_amt) as revenue
,rank() over(order by sum(ride_amt) desc) as rider_rank
from dim_cust as rd
join ride_fact as r
on rd.id = r.rider_id
group by 1;

# Bucket pick up locations by revenue (slow, average, busy)

select
landmark_name as pick_up_locations
,sum(ride_amt) as revenue
,case
when sum(ride_amt) < 150 then 'slow'
when sum(ride_amt) >= 150 and sum(ride_amt) < 230 then 'average'
when sum(ride_amt) >= 230 then 'busy'
else 'other' end as location_status
from dim_location as l
join ride_fact as r
on l.id = r.start_loc_id
group by 1
order by 2;

# Summary of ride time and distance by week

select
monthname(ride_start_time) as months
,week(ride_start_time) as weeks
,sum(miles) as distance
,sum(ride_amt) as revenue
from ride_fact
group by 1,2
having sum(ride_amt) > 0
order by 2;

# Bucket revenue by promotion by month

select
monthname(ride_start_time) as month
,promo_name
,sum(ride_amt) as revenue
from ride_fact as r
join dim_promo as p
on r.promo_id = p.id
group by 1,2
order by 3 desc;



# SELECT 1: Which Driver completed the most rides?

SELECT  Driver_ID, count(*) AS num_rides
FROM ride_fact
GROUP BY Driver_ID
ORDER BY count(*) DESC;

# SELECT 2: Which car manufacturer is most common for Ridex Drivers?

SELECT Brand, count(*) as num_cars
FROM dim_cab
GROUP BY Brand
ORDER BY count(*) DESC;

# SELECT 3: How many customers utilized promotions for their ride?

SELECT count(r.Promo_ID) as Num_Promo, r.Promo_ID, p.Promo_Name
FROM ride_fact r
JOIN dim_promo p ON r.Promo_ID = p.ID
GROUP BY r.Promo_ID
ORDER BY count(r.Promo_ID) DESC;

# SELECT 4: Show all riders with a bookmarked location and their total for the ride

SELECT Rider_ID, first_name, last_name, Bookmark_tag, trip_total
FROM (SELECT DISTINCT(cb.Rider_ID), c.first_name, c.last_name, cb.Bookmark_tag,
	SUM(r.ride_amt) AS trip_total
	FROM Dim_Cust c
	JOIN Dim_Cust_Bookmark cb ON c.ID = cb.Rider_ID
	JOIN Ride_Fact r ON c.ID = r.Rider_ID
	GROUP BY cb.Rider_ID, cb.Bookmark_tag) AS bookmarked
GROUP BY Rider_ID, Bookmark_tag, trip_total;

# SELECT 5: Show all rides where the rider left/went to a landmark,
	-- what is the total trip cost?

SELECT DISTINCT(r.Rider_ID), c.First_name, c.Last_name, l.Landmark_Name,
	r.ride_amt AS ride_cost
FROM ride_fact r
JOIN Dim_Location l ON r.Start_loc_ID = l.ID
JOIN Dim_Cust c ON r.Rider_ID = c.ID
WHERE Is_Landmark = 1
GROUP BY Rider_ID, First_Name, Last_name, landmark_Name, ride_amt;




# Show everything Dim_cust table where gender is Male, order by joined date

select *
from Dim_cust
order by joined_date;


# Show everything from Dim_account where customer paid by cash

select count(*)
from Dim_account
where payment_type = 'Ridex Cash';

# Show all customers with a bookmark of gym and groceries 

select c.ID, c.last_name, cb.bookmark_tag, cb.bookmark_loc_id
from Dim_cust as c
join dim_cust_bookmark cb on c.id = cb.rider_id
where (cb.bookmark_tag = 'grocery' or cb.bookmark_tag = 'gym')
order by c.ID;

# Show all customers that utilized promotion 3 only 

select surge_amt, base_amt, miles, ride_amt, zipcode, landmark_name
from ride_fact r
join dim_location dl on r.start_loc_id = dl.id
order by r.ID;

# Show total ride amount for rides which are greater than the average ride amount multiplied by 0.5

select *
from ride_fact
where ride_amt > 0.5 * 
	(select avg(ride_amt) 
		from ride_fact
        where promo_id = 0
    )
and promo_id = 0;


-- Rohit Jain
# 1. Show Overall Revenue/Sales by Calendar year and month ?
# 2 basic queries utilizing at least a where and/or group by clause */
Select SUM(Ride_amt) as `SalesbyMonth`, Dim_date.Year, dim_date.Month from 
ride_fact inner join dim_date
On ride_fact.date_id = dim_date.ID
Group by Dim_date.Year, dim_date.Month;

# 2. What is the Average Wait time for Riders after requesting the ride ? 
# Calculated Field as Wait Time in Seconds*/
Select 
dim_account.Account_no,
avg(timestampdiff(second,Request_time,Ride_start_time)) as Wait_time_seconds 
from ride_fact inner join dim_account
on ride_fact.Account_ID = dim_account.ID 
Group by dim_account.Account_no;

# 3. What Percentage of rides was cancelled after booking ? 
Using Subquery, group by and where clause */
select 
count(*) as Cancelled_CNT,
count(*) / rt.tot_cnt * 100 as `percentage`
from ride_fact rf cross join 
( select count(*) as tot_cnt from ride_fact) rt
where rf.ride_status = 'Cancelled'
group by rt.tot_cnt;

# 4. Show Top 3 Cab Drivers based on Revenue with their Driver & Car details ? 
Using CTE */
WITH CTE AS (
select distinct 
sum(Ride_AMT) OVER ( partition by driver_id) as total_Revenue, 
dim_driver.first_name,
dim_driver.last_name,
dim_cab.Brand,
dim_cab.Cab_type,
dim_cab.Model
from ride_fact 
inner join dim_driver 
on ride_fact.driver_id=dim_driver.Id
Inner join dim_cab
On ride_fact.cab_id = dim_cab.id
)
Select 
CTE.*,
dense_rank() over ( Order by total_Revenue desc) as rnk
from CTE
limit 3;

# 5. Show Total Number of trips & cumulative trips by date for each driver. Usage Running total and CTE*/
WITH CTE AS (
select distinct
ride_fact.driver_id, 
count(ride_fact.id) OVER ( partition by driver_id, dim_date.date
Order by dim_date.date) as Ridesperdate, 
dim_date.date,
dim_driver.first_name,
dim_driver.last_name,
dim_cab.Brand,
dim_cab.Cab_type,
dim_cab.Model
from ride_fact 
inner join dim_driver 
on ride_fact.driver_id=dim_driver.Id
Inner join dim_cab
On ride_fact.cab_id = dim_cab.id
Inner join dim_date
On ride_fact.date_ID=dim_date.ID
)
select 
driver_id,
SUM(Ridesperdate) OVER ( Order by DATE) as `running_total_rides`,
date, 
first_name,
last_name  
from CTE;


