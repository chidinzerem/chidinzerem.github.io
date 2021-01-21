### QUANTITATIVE METHDOS: Final project
### data analysis project using heart_failure_clinical_records_dataset to predict if someone who is having heart failure is going to die

library(data.table)
library(MASS)
library(pROC)
library(caret)

### import and look at data
data <- read.csv("~/Desktop/quantitative methods/heart_failure_clinical_records_dataset.csv")
dt <- as.data.table(data)
head(dt)
str(dt)

##plot a correlation matrix
cor(model)

### because predicting if death event or not, convert death_event to factor
dt$DEATH_EVENT <- as.factor(dt$DEATH_EVENT)

### run model on all of the variables
model <- glm(DEATH_EVENT~ ., data = dt, family = 'binomial', maxit = 100)
summary(model)

### use step AIC to get the most important varaibles
stepAIC(model)

### run the new recommended model
new_model <- glm(formula = DEATH_EVENT ~ age + ejection_fraction + serum_creatinine + 
                   serum_sodium + time, family = "binomial", data = dt, maxit = 100)

summary(new_model)

#make a prediction
preds <- predict(new_model, dt, type='response')

#Create a Roc curve and results for the prediction-based data
roc_curve <- roc(dt$DEATH_EVENT, preds)
roc_curve
plot(roc_curve)

#Calculate Threshold
thresh <- coords(roc=roc_curve, x = 'best', best.method = 'closest.topleft', transpose=TRUE)

## Prepare data for confusion matrix, round prediction values
rounded_preds <- as.factor(as.integer(preds > thresh[1]))
targets <- as.factor(as.integer(dt$type) - 1)

postResample(pred = rounded_preds, obs = targets)

#Build a confusion matrix to see results.
confusionMatrix(rounded_preds, targets, positive = '1')
