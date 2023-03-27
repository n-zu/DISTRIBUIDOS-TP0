package common

import (
	"bufio"
	"fmt"
	"net"
	"io"
	"strings"
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



// SendBets Sends a bet to the server and checks response
func sendBets( conn net.Conn, id string, betData []string) (string, error) {

	message := strings.Join(betData, ";")
	len := len(message)
	if len > 8192 { // Max 8kb
		return "", errors.New("Message too long")
	}

	// Send message length and then message 
	binary.Write(conn, binary.BigEndian, uint16(len))
	io.WriteString(conn, message)
	msg, err := bufio.NewReader(conn).ReadString('\n')
	msg = strings.TrimSpace(msg)

	if err == nil && msg != "OK" {
		return "", errors.New(fmt.Sprintf("Unexpected response: %v", msg))
	}

	return msg, err
}

func openSendBets(conn net.Conn, id string) {
	OPEN_MSG := "BETS"
	binary.Write(conn, binary.BigEndian, uint16(len(OPEN_MSG)))
	io.WriteString(conn, OPEN_MSG)
}

func closeSendBets(conn net.Conn, id string) {
	CLOSE_MSG := "CLOSE"
	binary.Write(conn, binary.BigEndian, uint16(len(CLOSE_MSG)))
	io.WriteString(conn, CLOSE_MSG)
	conn.Close()
}

func askForWinners(conn net.Conn, id string) ([]string, error){
	ASK_MSG := "ASK"
	binary.Write(conn, binary.BigEndian, uint16(len(ASK_MSG)))
	io.WriteString(conn, ASK_MSG)
	binary.Write(conn, binary.BigEndian, uint16(len(id)))
	io.WriteString(conn, id)
	msg, err := bufio.NewReader(conn).ReadString('\n')
	msg = strings.TrimSpace(msg)

	if err == nil && msg == "REFUSE" {
		return nil, errors.New("Server refused")
	}
	
	return strings.Split(msg, ","), err
}