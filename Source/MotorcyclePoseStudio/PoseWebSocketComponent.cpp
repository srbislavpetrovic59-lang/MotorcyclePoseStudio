#include "PoseWebSocketComponent.h"

#include "WebSocketsModule.h"
#include "Modules/ModuleManager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"


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
    if (StatusCode == 1000)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Pose WebSocket closed normally.")
        );
        return;
    }

    UE_LOG(
        LogTemp,
        Warning,
        TEXT(
            "Pose WebSocket closed. Code: %d, Reason: %s"
        ),
        StatusCode,
        *Reason
    );
}


void UPoseWebSocketComponent::HandleMessage(
    const FString& Message
)
{
    FRiderState RiderState;

    if (!ParseRiderState(Message, RiderState))
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("Pose WebSocket received invalid RiderState JSON.")
        );
        return;
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT(
            "RiderState: elbows %.1f / %.1f, "
            "knees %.1f / %.1f, torso %.1f, confidence %.2f"
        ),
        RiderState.LeftElbow,
        RiderState.RightElbow,
        RiderState.LeftKnee,
        RiderState.RightKnee,
        RiderState.TorsoAngle,
        RiderState.PoseConfidence
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

bool UPoseWebSocketComponent::ParseRiderState(
    const FString& Message,
    FRiderState& OutRiderState
) const
{
    TSharedPtr<FJsonObject> JsonObject;

    const TSharedRef<TJsonReader<>> Reader =
        TJsonReaderFactory<>::Create(Message);

    if (!FJsonSerializer::Deserialize(Reader, JsonObject) ||
        !JsonObject.IsValid())
    {
        return false;
    }

    double Value = 0.0;

    if (!JsonObject->TryGetNumberField(TEXT("left_elbow"), Value))
    {
        return false;
    }
    OutRiderState.LeftElbow = static_cast<float>(Value);

    if (!JsonObject->TryGetNumberField(TEXT("right_elbow"), Value))
    {
        return false;
    }
    OutRiderState.RightElbow = static_cast<float>(Value);

    if (!JsonObject->TryGetNumberField(TEXT("left_knee"), Value))
    {
        return false;
    }
    OutRiderState.LeftKnee = static_cast<float>(Value);

    if (!JsonObject->TryGetNumberField(TEXT("right_knee"), Value))
    {
        return false;
    }
    OutRiderState.RightKnee = static_cast<float>(Value);

    if (!JsonObject->TryGetNumberField(TEXT("torso_angle"), Value))
    {
        return false;
    }
    OutRiderState.TorsoAngle = static_cast<float>(Value);

    if (!JsonObject->TryGetNumberField(TEXT("pose_confidence"), Value))
    {
        return false;
    }
    OutRiderState.PoseConfidence = static_cast<float>(Value);

    return true;
}