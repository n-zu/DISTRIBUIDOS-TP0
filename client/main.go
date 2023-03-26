package main

import (
	"fmt"
	"strings"
	"time"
	"os"
	"os/signal"
	"encoding/csv"
	"syscall"

	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
	log "github.com/sirupsen/logrus"
	"github.com/spf13/viper"

	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common"
)

// InitConfig Function that uses viper library to parse configuration parameters.
// Viper is configured to read variables from both environment variables and the
// config file ./config.yaml. Environment variables takes precedence over parameters
// defined in the configuration file. If some of the variables cannot be parsed,
// an error is returned
func InitConfig() (*viper.Viper, error) {
	v := viper.New()

	// Configure viper to read env variables with the CLI_ prefix
	v.AutomaticEnv()
	v.SetEnvPrefix("cli")
	// Use a replacer to replace env variables underscores with points. This let us
	// use nested configurations in the config file and at the same time define
	// env variables for the nested configurations
	v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

	// Add env variables supported
	v.BindEnv("id")
	v.BindEnv("server", "address")
	v.BindEnv("loop", "period")
	v.BindEnv("loop", "lapse")
	v.BindEnv("log", "level")
	v.BindEnv("data", "file")
	v.BindEnv("data", "batchSize")

	// Try to read configuration from config file. If config file
	// does not exists then ReadInConfig will fail but configuration
	// can be loaded from the environment variables so we shouldn't
	// return an error in that case
	v.SetConfigFile("./config.yaml")
	if err := v.ReadInConfig(); err != nil {
		fmt.Printf("Configuration could not be read from config file. Using env variables instead")
	}

	// Parse time.Duration variables and return an error if those variables cannot be parsed
	if _, err := time.ParseDuration(v.GetString("loop.lapse")); err != nil {
		return nil, errors.Wrapf(err, "Could not parse CLI_LOOP_LAPSE env var as time.Duration.")
	}

	if _, err := time.ParseDuration(v.GetString("loop.period")); err != nil {
		return nil, errors.Wrapf(err, "Could not parse CLI_LOOP_PERIOD env var as time.Duration.")
	}

	return v, nil
}

// InitLogger Receives the log level to be set in logrus as a string. This method
// parses the string and set the level to the logger. If the level string is not
// valid an error is returned
func InitLogger(logLevel string) error {
	level, err := logrus.ParseLevel(logLevel)
	if err != nil {
		return err
	}

    customFormatter := &logrus.TextFormatter{
      TimestampFormat: "2006-01-02 15:04:05",
      FullTimestamp: false,
    }
    logrus.SetFormatter(customFormatter)
	logrus.SetLevel(level)
	return nil
}

// PrintConfig Print all the configuration parameters of the program.
// For debugging purposes only
func PrintConfig(v *viper.Viper) {
	logrus.Infof("action: config | result: success | client_id: %s | server_address: %s | loop_lapse: %v | loop_period: %v | log_level: %s",
	    v.GetString("id"),
	    v.GetString("server.address"),
	    v.GetDuration("loop.lapse"),
	    v.GetDuration("loop.period"),
	    v.GetString("log.level"),
    )
}

// Returns a function that takes the amount of lines to read from file as parameter and returns them as a string array
// If there are no more lines to read, the function returns an empty array and closes the file if open
func GetGetBetData(fileName string, id string) func(int) []string {
	file, err := os.Open(fileName)
	if err != nil {
		log.Fatalf("Could not open file %s: %s", fileName, err)
	}
	log.Debugf("action: open_file %v | result: success | client_id: %v", fileName, id)
	reader := csv.NewReader(file)

	return func(lines int) []string {
		
		data := make([]string, 0, lines)
		for i := 0; i < lines; i++ {
			line, err := reader.Read()
			if err != nil {
				// If there are no more lines to read, close the file and return an empty array
				file.Close()
				log.Debugf("action: close_file %v | result: success | client_id: %v", fileName, id)
				return data
			}
			data = append(data, line...)
		}
		return data

	}
}

func main() {
	v, err := InitConfig()
	if err != nil {
		log.Fatalf("%s", err)
	}

	if err := InitLogger(v.GetString("log.level")); err != nil {
		log.Fatalf("%s", err)
	}

	// Print program config with debugging purposes
	PrintConfig(v)

	clientConfig := common.ClientConfig{
		ServerAddress: v.GetString("server.address"),
		ID:            v.GetString("id"),
		LoopLapse:     v.GetDuration("loop.lapse"),
		LoopPeriod:    v.GetDuration("loop.period"),
		BatchSize: 		 v.GetInt("data.batchSize"),
	}

	// Create a channel that is notified on SIGTERM
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGTERM)

	getBetData := GetGetBetData(v.GetString("data.file"), clientConfig.ID)
	client := common.NewClient(clientConfig, getBetData)
	client.StartClientLoop(sigChan)
}
