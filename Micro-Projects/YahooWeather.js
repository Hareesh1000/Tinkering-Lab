const axios = require('axios');
const mongoose = require('mongoose');

// Database Connection
async function connectDB() {
  try {
    await mongoose.connect('mongodb://localhost:27017/training_projects');
    console.log('Connection established');
  } catch (err) {
    console.error('Error connecting to DB:', err);
  }
}

// Schema
const weatherSchema = new mongoose.Schema({
  weather_info: { type: mongoose.Schema.Types.Mixed  },
  generated_date: { type: Date },
});

const errorSchema = new mongoose.Schema({
        error_status :{type: String},
        error_code :{type: String},
        error_message : { type: mongoose.Schema.Types.Mixed  }, 
        generated_date: { type: Date },
})

// Model
const Weather = mongoose.model('Weather', weatherSchema);
const WeatherError = mongoose.model('WeatherError',errorSchema);

// Fetch Data from API
async function fetchWeatherData(city) {
  const options = {
    method: 'GET',
    url: 'https://yahoo-weather5.p.rapidapi.com/weather',
    params: {
      location: city,
      format: 'json',
      u: 'f',
    },
    headers: {
      'x-rapidapi-key': '854c7f5dadmshb4240982d033359p1500f3jsn1c167571dfc9',
      'x-rapidapi-host': 'yahoo-weather5.p.rapidapi.com',
    },
  };

  try {
    const response = await axios.request(options);
    return response.data;
  } catch (error) {
            const newError = new WeatherError({
                    error_status :error.status,
                    error_code :error.code,
                    error_message :error.response.data,
                    generated_date: new Date(),
            })
            await newError.save();
            console.log(`New error is saved`);
  }
}

// Save data in the database
async function saveInDatabase(data) {
  if (!data) {
    console.log('No data to save, skipping...');
    return;
  }

  try {
    const newWeather = new Weather({
      weather_info: data,
      generated_date: new Date(),
    });

    const savedWeather = await newWeather.save();
    console.log('Weather data saved:');
  } catch (error) {
    console.error('Error saving data:', error);
  }
}

// Main function
async function main() {
  await connectDB();
  
  const city = 'Chennai';
  const weatherData = await fetchWeatherData(city);

  await saveInDatabase(weatherData);

  mongoose.connection.close();
  console.log('End of script');
}

main();
