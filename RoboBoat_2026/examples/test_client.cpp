#include <chrono>
#include <cstring>
#include <iostream>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include "../msgs/report.pb.h"


int main()
{
    using namespace std::chrono;
    // creating socket
    int clientSocket = socket(AF_INET, SOCK_STREAM, 0);

    // specifying address
    sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(50000);
    serverAddress.sin_addr.s_addr = INADDR_ANY;

    // sending connection request
    connect(clientSocket, (struct sockaddr*)&serverAddress,
            sizeof(serverAddress));

    // building report message
    robocommand::roboboat::v1::Report report;
    report.set_team_id("GOAT");
    report.set_vehicle_id("Bob-01");
    report.set_seq(42);
    time_point now = system_clock::now();
    auto time_since_epoch = now.time_since_epoch();
    auto duration_s = duration_cast<seconds>(time_since_epoch);
    auto duration_ns = duration_cast<nanoseconds>(time_since_epoch-duration_s);
    google::protobuf::Timestamp* ts = report.mutable_sent_at();
    ts->set_seconds(duration_s.count());
    ts->set_nanos(duration_ns.count());
    robocommand::roboboat::v1::GatePass* gp = report.mutable_gate_pass();
    gp->set_type(robocommand::roboboat::v1::GATE_ENTRY);
    robocommand::roboboat::v1::LatLng* latlng = gp->mutable_position();
    latlng->set_latitude(27.331234);
    latlng->set_longitude(-82.560123);

    // formatting message
    std::string msg = report.SerializeAsString();
    uint8_t msg_len = uint8_t(report.ByteSizeLong());

    // sending 2-byte header
    send(clientSocket, "$R", 2, 0);

    // sending 1-byte length
    send(clientSocket, &msg_len, sizeof(msg_len), 0);

    // sending serialized report message
    send(clientSocket, msg.c_str(), msg_len, 0);

    // sending 2-byte footer
    send(clientSocket, "!!", 2, 0);

    // closing socket
    close(clientSocket);

    return 0;
}