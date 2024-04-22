import { Socket } from "socket.io";
import express, { Express, Request, Response } from 'express';

require('dotenv').config();

const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");

const io = new Server(server, {
    cors: {
        origin: process.env.ORIGIN,
        methods: ["GET", "POST"],
        credentials: true,
        allowedHeaders: ["Authorization", "Content-Type"],
    }
});

io.on('connection', (socket: Socket) => {
    socket.on('joinRoom', ([roomId]) => {
        let playersInRoom = io.sockets.adapter.rooms.get(roomId)?.size ?? 0

        // if there arent 2 players already in the room
        if (playersInRoom < 2) {
            socket.join(roomId);
            console.log('a user connected: ' + socket.id);
            console.log(playersInRoom)
            if (playersInRoom == 1)
                io.in(roomId).emit("startMatch")
        }
        else
            console.log("room si full")

        socket.on('error', function (err) {
            console.log(err);
        });

        //implement disconnect
    })
});

server.listen(process.env.PORT, () => {
    console.log('listening on port 5000');
});