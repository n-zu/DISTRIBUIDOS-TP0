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
	LoopPeriod    time.Duration
	BatchSize     int
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	getBetData func(int) []string
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, getBetData func(int) []string) *Client {
	client := &Client{
		config: config,
		getBetData: getBetData,
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

// StartSendBets Starts sending bets to the server in a loop
func (c *Client) startSendBets(sigChan chan os.Signal) {
	c.createClientSocket()

	openSendBets(c.conn, c.config.ID)

	loop: for {
		betData := c.getBetData(c.config.BatchSize)
		if len(betData) == 0 {
			break
		}

		_, err := sendBets(c.conn, c.config.ID, betData)

		if err == nil {
			log.Infof("action: apuestas_enviadas | result: success " )
		} else {
			log.Infof("action: apuestas_enviadas | result: fail | %v", err.Error() )
		}

		select {
			case <- sigChan:
				break loop
			default:
		}
	}

	closeSendBets(c.conn, c.config.ID)
	log.Debugf("action: close_connection | result: success | client_id: %v", c.config.ID)
}

// StartAskForWinners Starts asking for winners to the server in a loop
func (c *Client) startAskForWinners(sigChan chan os.Signal) {

	loop: for {
		select {
			case <- sigChan:
				break loop
			case <- time.After(c.config.LoopPeriod):
		}
		c.createClientSocket()

		winners, err := askForWinners(c.conn, c.config.ID)

		if err == nil {
			log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v %v", len(winners), winners)
			c.conn.Close()
			break loop
		} else {
			log.Infof("action: consulta_ganadores | result: fail | %v", err.Error() )
		}

		c.conn.Close()
	}
}

// StartClientLoop sends bets and asks for winners
func (c *Client) StartClientLoop(sigChan chan os.Signal) {

	c.startSendBets(sigChan)
	c.startAskForWinners(sigChan)
}

