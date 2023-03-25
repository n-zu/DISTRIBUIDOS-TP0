package common

import (
	"bufio"
	"fmt"
	"net"
	"time"
	"os"
	"io"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// BetData Data used to bet
type BetData struct {
	Name 				string
	LastName 		string
	Document 		string
	BirthDate 	string
	Number 			string
}

func formatBetData(betData BetData) string {
	return fmt.Sprintf(
		"%s,%s,%s,%s,%s\n",
		betData.Name,
		betData.LastName,
		betData.Document,
		betData.BirthDate,
		betData.Number,
	)
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
	
	/*
	// autoincremental msgID to identify every message sent
	msgID := 1
loop:
	// Send messages if the loopLapse threshold has not been surpassed
	for timeout := time.After(c.config.LoopLapse); ; {

		// Create the connection the server in every loop iteration. Send an
	*/
		c.createClientSocket()

		io.WriteString(c.conn, formatBetData(c.betData))
		msg, err := bufio.NewReader(c.conn).ReadString('\n')
		// msgID++
		c.conn.Close()
		
		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v", c.config.ID, err,)
			log.Debugf("action: close_connection | result: success | client_id: %v", c.config.ID)
			return
		}
		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v", c.config.ID, msg, )
		log.Debugf("action: close_connection | result: success | client_id: %v", c.config.ID)
/*
		select {
			case <-timeout:
				log.Infof("action: timeout_detected | result: success | client_id: %v",c.config.ID,)
				break loop
			case <-sigChan:
				log.Infof("action: sigterm_detected | result: shutdown | client_id: %v",c.config.ID,)
				break loop
			case <-time.After(c.config.LoopPeriod):
		}
	}

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
	*/
}
