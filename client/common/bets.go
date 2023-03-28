package common

import (
	"bufio"
	"fmt"
	"net"
	"io"
	"errors"
	"encoding/binary"
)

// BetData Data used to bet
type BetData struct {
	Name 				string
	LastName 		string
	Document 		string
	BirthDate 	string
	Number 			string
}

// composeMessage Composes a string message to be sent to the server
func composeMessage(id string, betData BetData) string {
	return fmt.Sprintf(
		"%s,%s,%s,%s,%s,%s\n",
		id,
		betData.Name,
		betData.LastName,
		betData.Document,
		betData.BirthDate,
		betData.Number,
	)
}

// SendBets Sends a bet to the server and checks response
func sendBets( conn net.Conn, id string, betData BetData) (string, error) {

	message := composeMessage(id, betData)
	len := len(message)
	if len > 8192 { // Max 8kb
		return "", errors.New("Message too long")
	}

	// send message length and then message 
	binary.Write(conn, binary.BigEndian, uint16(len))
	io.WriteString(conn, composeMessage(id, betData))
	msg, err := bufio.NewReader(conn).ReadString('\n')
	return msg, err
}