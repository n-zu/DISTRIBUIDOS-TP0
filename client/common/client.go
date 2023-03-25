package common

import (
	"net"
	"time"
	"os"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	betData BetData
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, betData BetData) *Client {
	client := &Client{
		config: config,
		betData: betData,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
	        "action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	} else {
		log.Debugf("action: connect | result: success | client_id: %v", c.config.ID)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop(sigChan chan os.Signal) {
	
		c.createClientSocket()

		msg, err := sendBets(c.conn, c.config.ID, c.betData)

		if err == nil || msg != c.betData.Number {
			log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v", c.betData.Document, c.betData.Number, )
		} else {
			log.Infof("action: apuesta_enviada | result: fail | dni: %v | numero: %v", c.betData.Document, c.betData.Number, )
		} 
			
		c.conn.Close()
		log.Debugf("action: close_connection | result: success | client_id: %v", c.config.ID)
}

