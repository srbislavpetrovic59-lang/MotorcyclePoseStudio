#include "PoseWebSocketComponent.h"

#include "WebSocketsModule.h"
#include "Modules/ModuleManager.h"


UPoseWebSocketComponent::UPoseWebSocketComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}


void UPoseWebSocketComponent::BeginPlay()
{
    Super::BeginPlay();

    Connect();
}


void UPoseWebSocketComponent::Connect()
{
    FModuleManager::LoadModuleChecked<FWebSocketsModule>("WebSockets");

    WebSocket = FWebSocketsModule::Get().CreateWebSocket(
        TEXT("ws://127.0.0.1:8765")
    );

    WebSocket->OnConnected().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleConnected
    );

    WebSocket->OnConnectionError().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleConnectionError
    );

    WebSocket->OnClosed().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleClosed
    );

    WebSocket->OnMessage().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleMessage
    );

    UE_LOG(
        LogTemp,
        Display,
        TEXT("Pose WebSocket: connecting to ws://127.0.0.1:8765")
    );

    WebSocket->Connect();
}


void UPoseWebSocketComponent::HandleConnected()
{
    UE_LOG(
        LogTemp,
        Display,
        TEXT("Pose WebSocket: connected")
    );
}


void UPoseWebSocketComponent::HandleConnectionError(
    const FString& Error
)
{
    UE_LOG(
        LogTemp,
        Error,
        TEXT("Pose WebSocket connection error: %s"),
        *Error
    );
}


void UPoseWebSocketComponent::HandleClosed(
    int32 StatusCode,
    const FString& Reason,
    bool bWasClean
)
{
    UE_LOG(
        LogTemp,
        Warning,
        TEXT("Pose WebSocket closed. Code: %d, Reason: %s"),
        StatusCode,
        *Reason
    );
}


void UPoseWebSocketComponent::HandleMessage(
    const FString& Message
)
{
    UE_LOG(
        LogTemp,
        Display,
        TEXT("Pose WebSocket received: %s"),
        *Message
    );
}


void UPoseWebSocketComponent::TickComponent(
    float DeltaTime,
    ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction
)
{
    Super::TickComponent(
        DeltaTime,
        TickType,
        ThisTickFunction
    );
}