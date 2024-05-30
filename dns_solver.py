#### para correr ejecutar en terminal: python dns_solver.py www.harvard.edu 

import socket
import sys
from scapy.all import DNS, DNSQR, DNSRR, IP, UDP

# def send_dns_query(server, query_name):
#     query = DNS(rd=0, qd=DNSQR(qname=query_name, qtype='A'))
#     raw_query = bytes(query)

#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.settimeout(5)
#     sock.sendto(raw_query, (server, 53))

#     try:
#         data, _ = sock.recvfrom(512)
#         response = DNS(data)
#         return response
#     except socket.timeout:
#         print(f"Request to {server} timed out.")
#         return None
#     finally:
#         sock.close()

def send_dns_query(server_ip, dominio):
    query=DNS(rd=1, qd=DNSQR(qname=dominio, qtype="A")) #creo el paquete DNS con scapy
    
    socketsito=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #creo el socket UDP con direcciones IPv4
    socketsito.sendto(bytes(query), (server_ip,53)) #envio mi paquete DNS al socket con la ip y puerto correspondiente

    data, no_me_importa_nada = socketsito.recvfrom(512) #espero la respuesta del socket

    socketsito.close() #lo cierro de prepo

    return DNS(data) #me quedo con la data de la respuesta

def resolve_dns_aux(domain, servers):
    if not servers:
        print("No further nameservers found.")
        return []

    server = servers[0]
    response = send_dns_query(server, domain)   # enviamos consulta a primer servidor de la lista
    
    if response: 
        if response.an:    # para respuestas
            addresses = []
            for i in range(response.ancount):
                aux = response.an[i]
                if aux.type == 1:  # A record
                    addresses.append(aux.rdata)
                elif aux.type == 5:  # CNAME record y resolvemos este dominio
                    cname = aux.rdata
                    return resolve_dns(cname)
            return addresses
        elif response.ns:  # para autoritativos y resolvemos dns recursivamente
            new_servers = []
            for i in range(response.nscount):
                aux = response.ns[i]
                if aux.type == 2:
                    new_servers.append(aux.rdata)
            if new_servers:
                return resolve_dns_aux(domain, new_servers)
        elif response.ar:  # para adicionales y resolvemos dns recursivamente
            new_servers = []
            for i in range(response.arcount):
                aux = response.ar[i]
                if aux.type == 1:
                    new_servers.append(aux.rdata)
            if new_servers:
                return resolve_dns_aux(domain, new_servers)
        
    #return resolve_dns_aux(domain, new_servers) sino conseguimos rta, recursivamente con la lista de servidores restante (omitido el primero).


def resolve_dns(domain):
    return resolve_dns_aux(domain, ["199.9.14.201"])

# def resolve_dns_2(domain, server):

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dns_solver.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    addresses = resolve_dns(domain)
    if addresses:
        print(f"IP addresses for {domain}: {addresses}")
    else:
        print(f"Could not resolve {domain}")